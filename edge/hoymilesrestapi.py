""" Hoymiles REST API

"""

import logging
from datetime import date, datetime
from string import Template

import requests

from const import (
    BASE_URL,
    COOKIE_UID,
    DATA_FIND_DETAILS,
    GET_ALL_DEVICE_API,
    GET_DATA_API,
    HEADER_DATA,
    PAYLOAD_DETAILS,
    PAYLOAD_ID,
    PAYLOAD_T2,
    STATION_FIND,
)

module_logger = logging.getLogger("HoymilesAdd-on.hoymilesrestapi")


class HoymilesRestApi:
    """Hoymiles REST API"""

    def __init__(self, plant_id: str, token: str) -> None:
        self.session = requests.Session()
        self.session.headers = HEADER_DATA
        self.plant_id = plant_id
        self.token = token

    def _get(self, url: str, payload) -> requests.Response:
        """REST API get request

        :param url: URL for REST API request
        :type url: str
        :param payload: prepared payload
        :type payload: _type_
        :return: _description_
        :rtype: requests.Response
        """
        try:
            response = self.session.get(
                url, data=payload.replace("\n", "").encode("utf-8")
            )
            return response
        except requests.exceptions.HTTPError as errh:
            module_logger.error(errh)
        except requests.exceptions.ConnectionError as errc:
            module_logger.error(errc)
        except requests.exceptions.Timeout as errt:
            module_logger.error(errt)
        except requests.exceptions.RequestException as err:
            module_logger.error(err)
        return requests.Response()

    def _post(self, url, payload) -> requests.Response:
        """REST API post request

        :param url: URL for REST API request
        :type url: str
        :param payload: prepared payload
        :type payload: _type_
        :return: _description_
        :rtype: requests.Response
        """
        try:
            response = self.session.post(
                url, data=payload.replace("\n", "").encode("utf-8")
            )
            return response
        except requests.exceptions.HTTPError as errh:
            module_logger.error(errh)
        except requests.exceptions.ConnectionError as errc:
            module_logger.error(errc)
        except requests.exceptions.Timeout as errt:
            module_logger.error(errt)
        except requests.exceptions.RequestException as err:
            module_logger.error(err)
        return requests.Response()

    def _options(self, url: str, payload) -> requests.Response:
        """REST API option request

        :param url: URL for REST API request
        :type url: str
        :param payload: prepared payload
        :type payload: _type_
        :return: _description_
        :rtype: requests.Response
        """
        try:
            response = self.session.options(
                url, data=payload.replace("\n", "").encode("utf-8")
            )
            return response
        except requests.exceptions.HTTPError as errh:
            module_logger.error(errh)
        except requests.exceptions.ConnectionError as errc:
            module_logger.error(errc)
        except requests.exceptions.Timeout as errt:
            module_logger.error(errt)
        except requests.exceptions.RequestException as err:
            module_logger.error(err)
        return requests.Response()

    def request_solar_data(self):
        """Send request for solar data

        :return: REST API response
        :rtype: _type_
        """
        payload = self.prepare_payload_t2()
        self.prepare_cookies()
        response = self._post(BASE_URL + GET_DATA_API, payload)
        return response

    def prepare_payload_t2(self):
        """Prepare payload T2 type

        :return: prepared payload
        :rtype: _type_
        """
        template = Template(PAYLOAD_T2)
        payload = template.substitute(sid=self.plant_id)
        return payload

    def prepare_cookies(self):
        """Prepare common cookies in header."""
        self.session.headers["Cookie"] = (
            COOKIE_UID
            + "; hm_token="
            + self.token
            + "; Path=/; Domain=.global.hoymiles.com;"
            + f"Expires=Sat, 30 Mar {date.today().year + 1} 22:11:48 GMT;"
            + "'"
        )

    def get_plant_hw(self):
        """Send request for getting hardware plant list.

        :return: REST API response
        :rtype: _type_
        """
        payload = self.prepare_payload_id()
        self.prepare_cookies()
        response = self._post(BASE_URL + GET_ALL_DEVICE_API, payload)
        return response

    def prepare_payload_id(self):
        """Preparing payload ID

        :return: prepared payload
        :rtype: _type_
        """
        template = Template(PAYLOAD_ID)
        payload = template.substitute(id=self.plant_id)
        return payload

    def find_station(self):
        """Find power plant - usually used to verify if plant id is correct.

        :return: REST API response
        :rtype: _type_
        """
        payload = self.prepare_payload_id()
        self.prepare_cookies()
        response = self._post(BASE_URL + STATION_FIND, payload)
        return response

    def get_alarm(self, micro_id: str, micro_sn: str):
        """Get micro inverter alarms

        :param micro_id: micro inverter id
        :type micro_id: str
        :param micro_sn: micro inverter serial number
        :type micro_sn: str
        :return: REST API response
        :rtype: _type_
        """
        payload = self.prepare_payload_details(micro_id, micro_sn)

        self.prepare_cookies()
        response = self._post(BASE_URL + DATA_FIND_DETAILS, payload)
        return response

    def prepare_payload_details(self, micro_id: str, micro_sn: str):
        """Preparing specific payload used to get plant configuration details

        :param micro_id: micro inverter id
        :type micro_id: str
        :param micro_sn: micro inverter serial number
        :type micro_sn: str
        :return: prepared payload
        :rtype: _type_
        """
        template = Template(PAYLOAD_DETAILS)
        payload = template.substitute(
            mi_id=micro_id,
            mi_sn=micro_sn,
            sid=self.plant_id,
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        return payload
