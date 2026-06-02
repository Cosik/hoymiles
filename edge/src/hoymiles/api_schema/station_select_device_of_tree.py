from __future__ import annotations

from pydantic import BaseModel


class DeviceTree(BaseModel):
    status: int
    message: str
    data: list[DevicedDict] | None = []
    systemNotice: str | None = None


class DevicedDict(BaseModel):
    id: int
    sn: str | int | None = None
    text: str | None = None

    dtu_sn: str | int | None = None
    type: int
    model_no: str | int | None = None
    soft_ver: str | None = None
    hard_ver: str | None = None
    warn_data: WarnDict | dict | None = None
    children: list[DevicedDict] | None = []


class WarnDict(BaseModel):
    connect: bool
    warn: bool
