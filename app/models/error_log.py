from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.base import Base

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    level = Column(String, nullable=False)       # e.g., 'ERROR', 'WARNING'
    location = Column(String, nullable=False)    # e.g., 'auth.py:login_user'
    message = Column(String, nullable=False)     # summary
    details = Column(Text, nullable=True)        # traceback or extra context
