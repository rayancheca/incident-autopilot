from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from app.models.reports import IRReport


class WSMessageType(StrEnum):
    TOKEN = "token"
    STATUS = "status"
    ERROR = "error"
    FINAL = "final"


class WSToken(BaseModel):
    type: WSMessageType = WSMessageType.TOKEN
    report_id: str
    token: str


class WSStatus(BaseModel):
    type: WSMessageType = WSMessageType.STATUS
    report_id: str
    status: str


class WSError(BaseModel):
    type: WSMessageType = WSMessageType.ERROR
    report_id: str
    message: str


class WSFinal(BaseModel):
    type: WSMessageType = WSMessageType.FINAL
    report_id: str
    report: IRReport
    metadata: dict[str, Any] = {}
