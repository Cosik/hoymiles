from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DataCountStationV1(BaseModel):
    status: int
    message: str
    data: DataDictv1
    systemNotice: str | None = None


class DataCountStation(BaseModel):
    status: int
    message: str
    data: DataDict | DataDictv1
    systemNotice: str | None = None


class DataDictv1(BaseModel):
    plant_id: int
    real_power: float
    today_eq: float
    month_eq: float
    year_eq: float | None = None
    total_eq: float
    co2_emission: float
    tree_planted: float
    data_time: str


class DataDict(BaseModel):
    today_eq: float
    month_eq: int
    year_eq: int | None = None
    total_eq: int
    real_power: float | None = None
    co2_emission_reduction: float
    plant_tree: int
    data_time: datetime
    last_data_time: datetime
    capacitor: float
    is_balance: int
    is_reflux: int
    reflux_station_data: RefluxDataDict | None = None


class RefluxDataDict(BaseModel):
    start_date: datetime | str | None = ""
    end_date: datetime | str | None = ""

    pv_power: float
    grid_power: float
    load_power: float
    bms_power: float
    bms_soc: float

    bms_out_eq: float
    bms_in_eq: float

    mb_in_eq: MBOut
    mb_out_eq: MBIn


class MBOut(BaseModel):
    today_eq: float
    month_eq: float
    year_eq: float
    total_eq: float


class MBIn(BaseModel):
    today_eq: float
    month_eq: float
    year_eq: float
    total_eq: float
