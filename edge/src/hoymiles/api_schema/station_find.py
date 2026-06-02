from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StationFind(BaseModel):
    status: int
    message: str
    data: DataDict | DataListV3
    systemNotice: str | None = None


class DataListV3(BaseModel):
    list: list[DataDictV3]
    total: int


class DataDictV3(BaseModel):
    id: int
    station_name: str
    capacity: float
    status: int
    location: str
    timezone: str


class DataDict(BaseModel):
    id: int
    gid: int
    name: str
    type: int
    tz_id: int
    city_code: str
    status: int
    create_by: int
    create_at: datetime
    classify: int
    tz_name: str
    pic_path: str
    capacitor: str
    address: str
    layout_step: int
    is_balance: int
    is_reflux: int
    remarks: str
    config: dict
    is_stars: int
    money_unit: str
    electricity_price: float
    in_price: float
    usd: str
    nk_name: str | None = None
    int5m: int
    city_id: int
    weather_of_cid: int
