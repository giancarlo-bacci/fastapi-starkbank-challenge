# Stark Bank Sandbox Integration (FastAPI)

This repository contains a small FastAPI application designed to integrate with **Stark Bank Sandbox** and fulfill the following assignment requirements.

## Assignment Requirements

1. Issue **8 to 12 Invoices every 3 hours for 24 hours** (Sandbox will emulate automatic payments for some invoices).
2. Receive the **webhook callback** for **Invoice credit** and send the received amount (minus eventual fees) to the target account using a **Transfer**:
   - **bank code:** 20018183
   - **branch:** 0001
   - **account:** 6341320293482496
   - **name:** Stark Bank S.A.
   - **tax ID:** 20.018.183/0001-80
   - **account type:** payment

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn
- APScheduler (interval-based job scheduling)
- Stark Bank Python SDK

## Project Structure

Current structure:

app/
  main.py                    # FastAPI app, routes, lifespan bootstrap
  scheduler.py               # APScheduler setup
  core/
    config.py                # Settings via environment variables
    starkbank_client.py      # StarkBank initialization/bootstrap
  services/
    invoice_service.py       # Business logic to create invoices (Task 1)
    transfer_service.py      # Business logic to create transfers (Task 2)
  jobs/
    invoicer.py              # Scheduled job that triggers invoice creation
  webhooks/
    invoice.py               # Webhook route handlers (Task 2)

## Local Development Setup (venv)

### 1) Create and activate a virtual environment

python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

### 2) Configure environment variables

Create a .env file (or export variables in your shell):

- STARKBANK_PROJECT_ID
- STARKBANK_PRIVATE_KEY_PATH
- STARKBANK_ENVIRONMENT (default: sandbox)

Example .env:

STARKBANK_PROJECT_ID=123456789
STARKBANK_PRIVATE_KEY_PATH=private_key.pem
STARKBANK_ENVIRONMENT=sandbox

### 3) Run the application

uvicorn app.main:app --host 127.0.0.1 --port 8000

Useful endpoints:
- GET /health – basic health check
- GET /docs – Swagger UI (TODO)
- /internal/run-job – manually trigger the invoice job (dev only; method may be GET or POST depending on your implementation)

## Scheduler

The invoicing job is scheduled with APScheduler.

### Test mode
For quick testing, the interval may be temporarily configured to run every 1 minute.

### Expected production-like configuration (for this assignment)
- Run every 3 hours
- On each run, issue 8–12 invoices to random people

Note: when running Uvicorn with --reload, the scheduler may start more than once due to the reloader process. For scheduler validation, run without --reload.

## Webhook Integration 

The application will expose a webhook endpoint to receive invoice credit events.
When an invoice is credited/paid, the app will:
1. Parse the webhook payload
2. Compute net amount (received amount minus eventual fees)
3. Create a Transfer to the target account defined in the assignment

## Production Considerations (Not implemented in this demo)

This project intentionally keeps the implementation simple to match the assignment scope. In a real production setup, I would apply:

1) Secret Management
- This demo reads the private key from a local file (*.pem) or by .env value (for convenience).
- In production, this should be stored in a secret manager (AWS/GCP/Azure) and injected securely.
- Secrets are managed via environment variables and never committed to the repository.

2) Scheduler Strategy
- APScheduler running inside a web server is acceptable for demos, but in production it can run multiple times if the service scales horizontally or uses multiple workers.
- In production, prefer:
  - an external scheduler (cron/EventBridge/Cloud Scheduler) calling a protected endpoint, or
  - a dedicated worker process + queue system.

3) Idempotency & Concurrency Control
- SQLite is used for simplicity. In production, this should be replaced with Postgres.
- Jobs and webhook handlers should be idempotent and protected against duplicates:
  - distributed locks (DB/Redis)
  - unique external_id keys when supported
  - consistent deduplication logic

4) Observability
- Replace print() with structured logging, add trace/correlation IDs, metrics, and alerting.

5) Reliability
- Use explicit timeouts, retry policies with exponential backoff, and error handling around third-party calls.

## Potential Documentation Improvement

While integrating with the Stark Bank Python SDK, an error was raised when the user object was not configured:

line 22, in check_user
    raise AssertionError("A user is required to access our API. Check our README: https://github.com/starkinfra/core-python/")
AssertionError: A user is required to access our API. Check our README: https://github.com/starkinfra/core-python/

However, the referenced repository (`starkinfra/core-python`) does not contain the SDK usage documentation.
The correct documentation for configuring the user and interacting with the API is available at:
https://github.com/starkbank/sdk-python

### Suggestion
Update the error message to point directly to the official SDK repository. This would improve developer experience and reduce confusion during the onboarding process.

## License
This repository is intended for evaluation purposes (technical assignment).