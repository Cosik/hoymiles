from __future__ import annotations

import uuid
from dataclasses import dataclass

from .api_schema.station_select_device_of_tree import DevicedDict

"""
types:
1 - dtu/dtu_pro
3 - micro inverter
6 - hybrid inverter
10 - bms

"""


@dataclass(repr=True)
class DevData:
    connect: bool = False

    alarm_code: int = 0
    alarm_string: str = ""
    loading: bool = True


class PlantObject:
    """Generic class for devices in plant"""

    data = DevData()

    def __init__(self, data: DevicedDict | dict) -> None:
        print(f"Creating PlantObject with data: {data}")
        if isinstance(data, DevicedDict):
            self.id = getattr(data, "id", None)  # pylint: disable=invalid-name
            self.sn = getattr(data, "sn", None)  # pylint: disable=invalid-name
            self.soft_ver = getattr(data, "soft_ver", None)  # pylint: disable=invalid-name
            self.hard_ver = getattr(data, "hard_ver", None)  # pylint: disable=invalid-name

        else:
            self.id = data.get("id", None)  # pylint: disable=invalid-name
            self.sn = data.get("sn", None)  # pylint: disable=invalid-name
            self.soft_ver = data.get("soft_ver", None)  # pylint: disable=invalid-name
            self.hard_ver = data.get("hard_ver", None)  # pylint: disable=invalid-name

        # TODO: Get more info about struct
        if isinstance(data, DevicedDict):
            if data.warn_data and data.warn_data.connect:
                self.data.connect = data.warn_data.connect
        self.uuid = str(uuid.uuid1())
        self.err_code = 0
        self.err_msg = ""


class Dtu(PlantObject):
    """Class representig DTU device"""

    def __init__(self, dtu_data: DevicedDict | dict) -> None:
        super().__init__(dtu_data)
        if isinstance(dtu_data, DevicedDict):
            self.model_no = getattr(dtu_data, "model_no", None)  # pylint: disable=invalid-name
        else:
            self.model_no = dtu_data.get("text", None)  # pylint: disable=invalid-name


class Micros(PlantObject):
    """Class representig Microinverter device"""

    data = DevData()

    def __init__(self, micro_data: DevicedDict | dict) -> None:
        super().__init__(micro_data)
        if isinstance(micro_data, DevicedDict):
            self.init_hard_no = getattr(micro_data, "model_no", None)  # pylint: disable=invalid-name
        else:
            self.init_hard_no = micro_data.get("text", None)


class BMS(PlantObject):
    """Class representig Microinverter device"""

    data = DevData()

    def __init__(self, bms_data: DevicedDict) -> None:
        super().__init__(bms_data)
        self.model = "battery"
        self.reserve_soc = 30
        self.max_power = 80
