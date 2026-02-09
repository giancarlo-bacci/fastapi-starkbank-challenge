import logging
import starkbank

logger = logging.getLogger(__name__)

TARGET_ACCOUNT = {
    "bank_code": "20018183",
    "branch_code": "0001",
    "account_number": "6341320293482496",
    "name": "Stark Bank S.A.",
    "tax_id": "20.018.183/0001-80",
    "account_type": "payment",
}


def create_transfer_for_invoice_credit(*, event_id: str, invoice_amount: int, invoice_fee: int | None):
    """
    Creates a transfer to the target account using the credited invoice amount minus eventual fees.
    """
    fee = invoice_fee or 0
    net_amount = invoice_amount - fee

    if net_amount <= 0:
        raise ValueError(f"Net amount must be positive. amount={invoice_amount} fee={fee}")

    external_id = f"transfer_{event_id}"

    transfer = starkbank.Transfer(
        amount=net_amount,
        name=TARGET_ACCOUNT["name"],
        tax_id=TARGET_ACCOUNT["tax_id"],
        bank_code=TARGET_ACCOUNT["bank_code"],
        branch_code=TARGET_ACCOUNT["branch_code"],
        account_number=TARGET_ACCOUNT["account_number"],
        account_type=TARGET_ACCOUNT["account_type"],
        external_id=external_id,
        description=f"Invoice credit webhook event {event_id}",
    )

    created = starkbank.transfer.create([transfer])

    # SDK usually returns a list
    created_transfer = created[0] if isinstance(created, list) and created else created

    logger.info(
        "Transfer created | event_id=%s transfer_id=%s net_amount=%s fee=%s",
        event_id,
        getattr(created_transfer, "id", None),
        net_amount,
        fee,
    )

    return created_transfer
