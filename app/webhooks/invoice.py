from fastapi import APIRouter, Header, HTTPException, Request
import starkbank
import logging
import time

from app.repositories.webhook_event_repo import try_register_event, delete_event
from app.services.transfer_service import create_transfer_for_invoice_credit


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/starkbank")
async def starkbank_webhook(
    request: Request,
    digital_signature: str | None = Header(default=None, alias="Digital-Signature"),
):
    start = time.perf_counter()
    VALID_LOG_TYPES = {"credited"}
    
    if not digital_signature:
        logger.warning("Missing Digital-Signature header")
        raise HTTPException(
            status_code=400,
            detail="Missing Digital-Signature header",
        )

    raw = await request.body()
    content = raw.decode("utf-8")

    # Valida a assinatura
    try:
        event = starkbank.event.parse(content=content, signature=digital_signature)
    except Exception as e:
        logger.warning("Invalid webhook signature", exc_info=e)
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature",
        )

    logger.info("Valid StarkBank webhook received | event_id=%s", event.id)

    # Só processa as invoices
    if event.subscription != "invoice":
        logger.info("Ignoring non-invoice event: %s", event.subscription)
        return {}

    log = event.log
    # verifica se foi realmente pago
    log_type = getattr(log, "type", None)

    invoice = log.invoice

    if log_type == "paid":
        logger.info("Invoice paid but not credited yet | invoice_id=%s", invoice.id)
        return {}


    if log_type not in VALID_LOG_TYPES:
        logger.info("Ignoring invoice event with type=%s", log_type)
        return {}

    # verifica se é novo
    is_new = try_register_event(event.id)
    if not is_new:
        logger.info("Duplicate webhook ignored | event_id=%s", event.id)
        return {}

    try:
        created_transfer = create_transfer_for_invoice_credit(
            event_id=event.id,
            invoice_amount=invoice.amount,
            invoice_fee=getattr(invoice, "fee", None),
        )
    except Exception:
        logger.exception("Transfer failed | event_id=%s invoice_id=%s", event.id, invoice.id)
        delete_event(event.id)  # permite retry do mesmo evento
        raise

    logger.info(
        "Webhook processed | event_id=%s invoice_id=%s transfer_id=%s",
        event.id,
        invoice.id,
        getattr(created_transfer, "id", None),
    )

    return {"received": True, "event_id": event.id, "transfer_id": getattr(created_transfer, "id", None)}

    elapsed = time.perf_counter() - start

    logger.info(
        "Webhook processed | event_id=%s invoice_id=%s elapsed=%.3fs",
        event.id,
        invoice.id,
        elapsed,
    )

    return {"received": True, "event_id": event.id}
