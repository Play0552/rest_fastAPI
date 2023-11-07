import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Status(enum.Enum):
    ok = 'работает'
    not_ok = 'не работает'
    unstable = 'работает нестабильно'


class ServiceCreate(BaseModel):
    name: str
    status: Status
    description: str


class ServiceUpdate(BaseModel):
    status: Status
    description: str


class ServiceGet(BaseModel):
    id: int
    name: str
    status: Status
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None


