from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.db import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    event_id = Column(String, primary_key=True, index=True)  # único
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
