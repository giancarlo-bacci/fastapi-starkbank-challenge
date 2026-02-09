from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.jobs.invoicer import run_job

scheduler = AsyncIOScheduler()

def start_scheduler():
    print("Starting scheduler...")
    scheduler.add_job(
        run_job,
        trigger="interval",
        hours=3,
        id="invoicer",
        replace_existing=True,
    )
    
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()