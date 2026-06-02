import os

import pytest
import requests
import yaml

# Paths to response data
RESP_BASE = os.path.join(os.path.dirname(__file__), "resp_data")
HW_BASE = os.path.join(RESP_BASE, "station_select_device_of_tree")
SOLAR_BASE = os.path.join(RESP_BASE, "data_count_station_real_data")
MICRO_BASE = os.path.join(RESP_BASE, "data_find_details")


class TestE2EHoymiles:
    """End-to-end tests for the Hoymiles Edge application."""

    @pytest.mark.parametrize(
        "scenario", [f for f in os.listdir(HW_BASE) if f.endswith(".json")]
    )
    def test_complete_poll_cycle(self, app_instance, mocker, scenario):
        """
        Test a full cycle of discovery and data polling.

        This verifies:
        1. Hardware discovery correctly identifies devices (DTUs, micros, BMS).
        2. Correct API versioning (V0/V3) and type mapping is used.
        3. Plant data pipeline transformations (kW calculation, casting) are applied.
        4. Data is fetched and published for all discovered devices to MQTT.
        """
        plant_id = "12345"  # From conftest.py HOYMILES_PLANT_ID

        # 1. Load data for the scenario
        with open(os.path.join(HW_BASE, scenario), "r") as f:
            hw_raw = yaml.safe_load(f)
            hw_data = hw_raw.get("data", [])

        # Load corresponding solar data (fallback to 1.json if scenario missing)
        solar_path = os.path.join(SOLAR_BASE, scenario)
        if not os.path.exists(solar_path):
            solar_path = os.path.join(SOLAR_BASE, "1.json")
        with open(solar_path, "r") as f:
            solar_data = yaml.safe_load(f).get("data", {})

        # For micro data, we use 1.json as a generic response
        with open(os.path.join(MICRO_BASE, "1.json"), "r") as f:
            micro_raw = yaml.safe_load(f)

        # 2. Mock CloudApi behavior to provide the test data
        # Reset api_version before each scenario
        app_instance.cloud_api.api_version = "0"

        mocker.patch.object(
            app_instance.cloud_api, "get_plant_hw", return_value=hw_data
        )
        mocker.patch.object(
            app_instance.cloud_api, "get_solar_data", return_value=solar_data
        )

        mock_micro_resp = mocker.Mock(spec=requests.Response)
        mock_micro_resp.json.return_value = micro_raw
        mock_micro_resp.status_code = 200
        mocker.patch.object(
            app_instance.cloud_api,
            "request_micro_details",
            return_value=mock_micro_resp,
        )

        # Set API version based on scenario (V3 changes type mappings)
        is_v3 = "3v" in scenario
        app_instance.cloud_api.api_version = "3" if is_v3 else "0"

        # Clear mocks to reset call history from any previous tests or init
        app_instance.mqtt_publisher.publish_discovery.reset_mock()
        app_instance.mqtt_publisher.publish_data.reset_mock()

        # 3. Perform Discovery phase
        app_instance._publish_discovery()

        # Verify Discovery was published to MQTT
        assert app_instance.mqtt_publisher.publish_discovery.called
        disc_calls = app_instance.mqtt_publisher.publish_discovery.call_args_list

        # Check plant discovery
        assert any(
            c.kwargs["device_type"] == "plant" and c.kwargs["device_id"] == plant_id
            for c in disc_calls
        )

        # Helper to collect expected device IDs from discovery logic
        def get_expected_ids(devices, v3):
            found = set()
            dtu_type = 2 if v3 else 1
            for dev in devices:
                d_type = dev.get("type")
                d_id = str(dev.get("id"))
                if d_type == dtu_type:
                    found.add(("dtu", d_id))
                elif d_type in (3, 6):
                    found.add(("micro", d_id))
                elif d_type == 10:
                    found.add(("bms", d_id))
                found.update(get_expected_ids(dev.get("children", []), v3))
            return found

        expected_devices = get_expected_ids(hw_data, is_v3)
        for d_type, d_id in expected_devices:
            assert any(
                c.kwargs["device_type"] == d_type and str(c.kwargs["device_id"]) == d_id
                for c in disc_calls
            )

        # 4. Perform Data Polling phase
        app_instance._fetch_and_publish_data()

        # 5. Verify Data Publication to MQTT
        data_calls = app_instance.mqtt_publisher.publish_data.call_args_list

        # Verify Plant Data
        plant_data_call = next(
            (c for c in data_calls if c.kwargs["device_id"] == plant_id), None
        )
        assert plant_data_call is not None
        p_payload = plant_data_call.kwargs["data"]

        # Check if plant_pipeline transformations were applied
        if "real_power" in solar_data and solar_data["real_power"] is not None:
            assert "real_power_kw" in p_payload
            # Pipeline casts real_power to float
            assert isinstance(p_payload["real_power"], float)
            expected_kw = round(float(solar_data["real_power"]) / 1000, 3)
            assert p_payload["real_power_kw"] == expected_kw

        # Verify Per-Micro Inverter Data publication
        micro_ids = app_instance.micro_ids_by_plant.get(plant_id, set())
        for m_id in micro_ids:
            m_call = next(
                (c for c in data_calls if str(c.kwargs["device_id"]) == str(m_id)), None
            )
            assert m_call is not None
            assert "connect" in m_call.kwargs["data"]
            assert "alarm_code" in m_call.kwargs["data"]

        # Verify BMS Data (if applicable)
        bms_ids = app_instance.bms_ids_by_plant.get(plant_id, set())
        if bms_ids and "reflux_station_data" in solar_data:
            for b_id in bms_ids:
                b_call = next(
                    (c for c in data_calls if str(c.kwargs["device_id"]) == str(b_id)),
                    None,
                )
                assert b_call is not None
