import os

import pytest
import requests
import yaml

# Path to response data files for micro inverter details, relative to project root
BASE_PATH = os.path.join(os.path.dirname(__file__), "resp_data", "data_find_details")


class TestMicroDataPipeline:
    """Tests for the micro inverter data extraction logic in HoymilesApplication."""

    @pytest.mark.parametrize(
        "file_name", [f for f in os.listdir(BASE_PATH) if f.endswith(".json")]
    )
    def test_fetch_and_publish_micro_data(self, app_instance, mocker, file_name):
        """
        Test _fetch_and_publish_micro_data using sample JSON data from data_find_details.

        This verifies:
        1. The application correctly requests details for each micro inverter.
        2. The _extract_micro_alarm_payload logic correctly parses net_state and alarms.
        3. The resulting data is published to the correct MQTT topic.
        """
        plant_id = "12345"
        micro_id = "98765"

        # 1. Mock micro IDs discovery for the plant to isolate the fetch logic
        mocker.patch.object(
            app_instance, "_get_micro_ids_for_plant", return_value=[micro_id]
        )

        # 2. Load sample data matching the DataFind schema
        file_path = os.path.join(BASE_PATH, file_name)
        with open(file_path, "r") as f:
            raw_response = yaml.safe_load(f)

        # 3. Mock CloudApi.request_micro_details to return our JSON data
        mock_resp = mocker.Mock(spec=requests.Response)
        mock_resp.json.return_value = raw_response
        mock_resp.status_code = 200
        mocker.patch.object(
            app_instance.cloud_api, "request_micro_details", return_value=mock_resp
        )

        # 4. Mock MQTT publisher to capture the final payload
        spy_publish = mocker.spy(app_instance.mqtt_publisher, "publish_data")

        # Execute the method under test
        app_instance._fetch_and_publish_micro_data(plant_id)

        # 5. Verify results
        assert spy_publish.call_count == 1
        call_args = spy_publish.call_args
        assert call_args.kwargs["device_id"] == micro_id

        payload = call_args.kwargs["data"]
        assert "connect" in payload
        assert "alarm_code" in payload
        assert "alarm_string" in payload

        # Validation based on raw input logic in _extract_micro_alarm_payload
        data_part = raw_response.get("data", {})
        assert payload["connect"] == bool(data_part.get("net_state", 0))

        warn_list = data_part.get("warn_list", [])
        if not warn_list:
            assert payload["alarm_code"] == 0
            assert payload["alarm_string"] == ""
