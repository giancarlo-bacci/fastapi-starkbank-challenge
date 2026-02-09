from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.scheduler import start_scheduler
from app.jobs.invoicer import run_job as job
from app.core.starkbank import get_starkbank
from app.webhooks.invoice import router as invoice_webhook_router
import logging
from app.db import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_starkbank()
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield

app = FastAPI(title="Stark API Teste", version="0.1.0", lifespan=lifespan)
app.include_router(invoice_webhook_router)

@app.get("/internal/run-job")
def run_job():
    job()
    return {"message": "Job rodou"}
    

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Olá"}

