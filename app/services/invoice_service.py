from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
import random
import starkbank
from faker import Faker
from validate_docbr import CNPJ
import uuid
import logging
import time

logger = logging.getLogger(__name__)

fake = Faker("pt_BR")
cnpj_generator = CNPJ()

def generate_customer():
    """
    Generate a random Brazilian company with valid CNPJ.
    """
    return {
        "name": fake.company(),
        "tax_id": cnpj_generator.generate(mask=True),
    }


def create_random_invoices(
    *,
    min_count: int = 8,
    max_count: int = 12,
    amount_cents: int = 10_000,
) -> List[starkbank.Invoice]:
    """
    Creates between min_count and max_count invoices with random recipients.
    """
    count = random.randint(min_count, max_count)

    due = datetime.utcnow() + timedelta(days=2)
    expiration_seconds = 60 * 60 * 24 * 7

    invoices = []

    for _ in range(count):
        customer = generate_customer()

        invoices.append(
            starkbank.Invoice(
                amount=amount_cents,
                due=due,
                expiration=expiration_seconds,
                fine=2.5,
                interest=1.3,
                name=customer["name"],
                tax_id=customer["tax_id"],
            )
        )

    return _create_with_retry(invoices)

def _create_with_retry(invoices_to_create, max_attempts: int = 5):
    for attempt in range(1, max_attempts + 1):
        try:
            logger.warning(f"[retry] attempt={attempt}")
            return starkbank.invoice.create(invoices_to_create)

        except Exception as e:
            print(f"[retry] attempt={attempt} error={e!r}")
            if attempt == max_attempts:

                raise

            # Exponential backoff + jitter
            sleep_s = (2 ** (attempt - 1)) + random.random()
            print(f"[retry] attempt={attempt} error={e!r} sleeping={sleep_s:.2f}s")
            time.sleep(sleep_s)
