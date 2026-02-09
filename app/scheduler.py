import os
import logging
from app.core.config import settings

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.jobs.invoicer import run_job

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
_started = False

def start_scheduler() -> None:
    """
    Start Scheduler only once and schedule the invoice job.
    Interval is controlled by INVOICE_INTERVAL_MINUTES (default: 180 = 3 hours).
    """
    global _started
    if _started:
        logger.info("Scheduler already started - skipping")
        return

    minutes = settings.invoice_interval_minutes

    logger.info("Starting scheduler | interval_minutes=%s", minutes)

    scheduler.add_job(
        run_job,
        trigger="interval",
        minutes=minutes,
        id="invoicer",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    scheduler.start()
    _started = True
    logger.info("Scheduler started")


def stop_scheduler() -> None:
    global _started
    if not _started:
        return

    logger.info("Stopping scheduler...")
    scheduler.shutdown(wait=False)
    _started = False
    logger.info("Scheduler stopped")
