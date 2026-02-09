from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from app.scheduler import start_scheduler
from app.jobs.invoicer import run_job as job
from app.core.starkbank import get_starkbank
from app.webhooks.invoice import router as invoice_webhook_router
import logging
from app.core.config import settings
from sqlalchemy.exc import OperationalError
from app.db import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init SDK 
    get_starkbank()

    logger.info("Application startup begin")

    # cria as tabelas SEMPRE no startup
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema ensured (create_all)")

    # scheduler
    enable_scheduler = settings.enable_scheduler
    if enable_scheduler:
        start_scheduler()
        logger.info("Scheduler enabled")
    else:
        logger.info("Scheduler disabled by env (ENABLE_SCHEDULER=false)")

    yield

app = FastAPI(title="Stark API Teste", version="0.1.0", lifespan=lifespan)
app.include_router(invoice_webhook_router)

@app.get("/internal/run-job")
def run_job():
    job()
    return {"message": "Job ran"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "StarkBank challenge API is running"}
