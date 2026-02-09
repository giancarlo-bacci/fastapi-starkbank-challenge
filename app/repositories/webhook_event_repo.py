from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.models.webhook_event import WebhookEvent

def try_register_event(event_id: str) -> bool:
    db = SessionLocal()
    try:
        db.add(WebhookEvent(event_id=event_id))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
    finally:
        db.close()

def delete_event(event_id: str) -> None:
    db = SessionLocal()
    try:
        obj = db.get(WebhookEvent, event_id)
        if obj:
            db.delete(obj)
            db.commit()
    finally:
        db.close()