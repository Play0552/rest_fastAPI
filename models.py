from datetime import datetime
from schemas import Status
from sqlalchemy import Enum

from sqlalchemy import Column, String, Integer, TIMESTAMP

from database import Base





class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    status = Column(Enum(Status), nullable=False)
    description = Column(String, nullable=False)
    start_time = Column(TIMESTAMP, default=datetime.utcnow)
    end_time = Column(TIMESTAMP, default=None)



