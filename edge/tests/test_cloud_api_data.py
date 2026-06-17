import os

import pytest
import requests
import yaml
from hoymiles.api_schema.data_count_station_real_data import (
    DataCountStation,
    DataCountStationV1,
)
from hoymiles.cloud_api import CloudApi

SOLAR_DATA_RESP_PATH = os.path.join(
    os.path.dirname(__file__), "resp_data", "data_count_station_real_data"
)

PLANT_HW_RESP_PATH = os.path.join(
    os.path.dirname(__file__), "resp_data", "station_select_device_of_tree"
)


class TestCloudApiSolarData:
    cloud_api: CloudApi

    def setup_method(self):
        # Initialize CloudApi with a mock config
        self.mock_config = {
            "HOYMILES_USER": "test_user",
            "HOYMILES_PASSWORD": "test_password",
            "HOYMILES_PLANT_ID": "12345",
            "USE_ESTAR": False,
            "EXPERIMENTAL_CUSTOM_API_URLS": False,
            "API_GATEWAY_BASE_URL": "",
            "API_VERSIONED_BASE_URL": "",
            "API_COOKIE_DOMAIN": "",
            "DEBUG_FORCE_API_VERSION": False,
            "DEBUG_API_VERSION": "",
        }
        self.cloud_api = CloudApi(self.mock_config)
        # Ensure token is set for subsequent requests
        self.cloud_api.connection.token = "mock_token_123"

    def _create_mock_response(self, status_code: int, json_data: dict):
        """Helper to create a mock requests.Response object."""
        mock_resp = requests.Response()
        mock_resp.status_code = status_code
        mock_resp.json = lambda: json_data
        return mock_resp

    @pytest.mark.parametrize(
        "file_name", ["1.json", "2.json", "3.json", "4.json", "5.json"]
    )
    def test_get_solar_data_success(self, mocker, file_name):
        """Test successful retrieval and parsing of solar data."""
        plant_id = "12345"

        file_path = os.path.join(SOLAR_DATA_RESP_PATH, file_name)
        with open(file_path, "r") as f:
            mock_solar_data_payload = yaml.safe_load(f)

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            return_value=self._create_mock_response(200, mock_solar_data_payload),
        )

        result = self.cloud_api.get_solar_data(plant_id)

        expected_data = DataCountStation.model_validate(
            mock_solar_data_payload
        ).data.model_dump()
        assert result == expected_data
        self.cloud_api._send_request.assert_called_once()

    @pytest.mark.parametrize("file_name", ["3v1.json"])
    def test_get_solar_data_success_v3(self, mocker, file_name):
        """Test successful retrieval and parsing of solar data (V3)."""
        plant_id = "12345"

        file_path = os.path.join(SOLAR_DATA_RESP_PATH, file_name)
        with open(file_path, "r") as f:
            mock_solar_data_payload = yaml.safe_load(f)

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            return_value=self._create_mock_response(200, mock_solar_data_payload),
        )

        result = self.cloud_api.get_solar_data(plant_id)

        expected_data = DataCountStationV1.model_validate(
            mock_solar_data_payload
        ).data.model_dump()
        assert result == expected_data

    def test_get_solar_data_token_expired_and_retry_success(self, mocker):
        """Test token expiration and successful retry."""
        plant_id = "12345"
        expired_token_payload = {"status": "100", "message": "token expired"}

        file_path = os.path.join(SOLAR_DATA_RESP_PATH, "1.json")
        with open(file_path, "r") as f:
            success_payload = yaml.safe_load(f)
            success_payload["status"] = 0

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            side_effect=[
                self._create_mock_response(200, expired_token_payload),
                self._create_mock_response(200, success_payload),
            ],
        )
        mocker.patch.object(self.cloud_api, "get_token", return_value=True)

        result = self.cloud_api.get_solar_data(plant_id)

        expected_data = DataCountStation.model_validate(
            success_payload
        ).data.model_dump()
        assert result == expected_data
        assert self.cloud_api._send_request.call_count == 2
        self.cloud_api.get_token.assert_called_once()

    def test_get_solar_data_schema_validation_failure(self, mocker):
        """Test when schema validation fails, it returns raw data."""
        plant_id = "12345"
        invalid_payload = {
            "status": "0",
            "message": "success",
            "data": {
                "today_eq": "not_a_float",
                "month_eq": 123,
                "total_eq": 12345,
                "real_power": 5000.0,
                "co2_emission_reduction": 2.5,
                "plant_tree": 10,
                "data_time": "2023-10-27T10:00:00",
                "last_data_time": "2023-10-27T09:55:00",
                "capacitor": 8000.0,
                "is_balance": 1,
                "is_reflux": 0,
            },
        }

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            return_value=self._create_mock_response(200, invalid_payload),
        )

        result = self.cloud_api.get_solar_data(plant_id)

        assert result == invalid_payload["data"]
        self.cloud_api._send_request.assert_called_once()

    def test_get_solar_data_api_error_status(self, mocker):
        """Test when API returns a non-success status other than token expired."""
        plant_id = "12345"
        error_payload = {"status": "1", "message": "some error occurred", "data": {}}

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            return_value=self._create_mock_response(200, error_payload),
        )

        result = self.cloud_api.get_solar_data(plant_id)

        assert result == {}
        self.cloud_api._send_request.assert_called_once()


class TestCloudApiPlantHw:
    cloud_api: CloudApi

    def setup_method(self):
        self.mock_config = {
            "HOYMILES_USER": "test_user",
            "HOYMILES_PASSWORD": "test_password",
            "HOYMILES_PLANT_ID": "12345",
            "USE_ESTAR": False,
        }
        self.cloud_api = CloudApi(self.mock_config)
        self.cloud_api.connection.token = "mock_token_123"

    def _create_mock_response(self, status_code: int, json_data: dict):
        mock_resp = requests.Response()
        mock_resp.status_code = status_code
        mock_resp.json = lambda: json_data
        return mock_resp

    @pytest.mark.parametrize("file_name", ["1.json", "2.json", "3.json", "3v1.json"])
    def test_get_plant_hw_success(self, mocker, file_name):
        """Test successful retrieval of hardware device tree."""
        plant_id = "12345"

        file_path = os.path.join(PLANT_HW_RESP_PATH, file_name)
        with open(file_path, "r") as f:
            mock_payload = yaml.safe_load(f)

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            return_value=self._create_mock_response(200, mock_payload),
        )

        result = self.cloud_api.get_plant_hw(plant_id)

        assert result == mock_payload.get("data")
        self.cloud_api._send_request.assert_called_once()

    def test_get_plant_hw_token_expired_and_retry_success(self, mocker):
        """Test token expiration and successful retry for hardware request."""
        plant_id = "12345"
        expired_token_payload = {"status": "100", "message": "token expired"}

        file_path = os.path.join(PLANT_HW_RESP_PATH, "1.json")
        with open(file_path, "r") as f:
            success_payload = yaml.safe_load(f)

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            side_effect=[
                self._create_mock_response(200, expired_token_payload),
                self._create_mock_response(200, success_payload),
            ],
        )
        mocker.patch.object(self.cloud_api, "get_token", return_value=True)

        result = self.cloud_api.get_plant_hw(plant_id)

        assert result == success_payload.get("data")
        assert self.cloud_api._send_request.call_count == 2
        self.cloud_api.get_token.assert_called_once()

    def test_get_plant_hw_api_error_status(self, mocker):
        """Test when API returns a non-success status."""
        plant_id = "12345"
        error_payload = {"status": "1", "message": "error", "data": []}

        mocker.patch.object(
            self.cloud_api,
            "_send_request",
            return_value=self._create_mock_response(200, error_payload),
        )

        result = self.cloud_api.get_plant_hw(plant_id)

        assert result == []
        self.cloud_api._send_request.assert_called_once()
