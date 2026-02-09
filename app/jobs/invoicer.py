from datetime import datetime
from app.services.invoice_service import create_random_invoices


def run_job():
    try:
        invoices = create_random_invoices()

        for inv in invoices:
            print(inv)

        print(f"Invoicer ran at (UTC): {datetime.utcnow().isoformat()}")

    except Exception as e:
        print(f"Erro no invoicer: {e!r}")
