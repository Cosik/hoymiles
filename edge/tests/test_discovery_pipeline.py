import os

import pytest
import yaml

# Path to response data files for device tree, relative to project root
BASE_PATH = os.path.join(
    os.path.dirname(__file__), "resp_data", "station_select_device_of_tree"
)


class TestDiscoveryPipeline:
    """Tests for the discovery publishing logic in HoymilesApplication."""

    @pytest.mark.parametrize(
        "file_name", [f for f in os.listdir(BASE_PATH) if f.endswith(".json")]
    )
    def test_publish_discovery(self, app_instance, mocker, file_name):
        """
        Test _publish_discovery using sample JSON data from station_select_device_of_tree.


        This verifies:
        1. Plant discovery is published.
        2. DTU discovery is published if present.
        3. Micro inverter discovery is published if present.
        4. BMS discovery is published if present.
        5. Internal ID caches (micro_ids_by_plant, bms_ids_by_plant) are populated correctly.
        """
        plant_id = "12345"  # Matches HOYMILES_PLANT_ID configured in conftest.py

        # 1. Load sample data
        file_path = os.path.join(BASE_PATH, file_name)
        with open(file_path, "r") as f:
            raw_response = yaml.safe_load(f)
            # The app calls get_plant_hw which returns the 'data' part of the response
            mock_hw_data = raw_response.get("data", [])

        # 2. Mock CloudApi.get_plant_hw to return our sample data
        mocker.patch.object(
            app_instance.cloud_api, "get_plant_hw", return_value=mock_hw_data
        )
        mocker.patch.object(
            app_instance.cloud_api, "get_plant_hw", return_value=mock_hw_data
        )

        # 2b. If file name contains '3v1', simulate API V3 behavior
        is_v3 = "3v" in file_name
        if is_v3:
            app_instance.cloud_api.api_version = "1"

        # 3. Mock MQTT publisher's publish_discovery method to capture calls
        spy_discovery = mocker.spy(app_instance.mqtt_publisher, "publish_discovery")

        # Execute the method under test
        app_instance._publish_discovery()

        # 4. Verify results
        # At minimum, one call for the plant itself must happen
        assert spy_discovery.called

        # Extract actual discoveries from the spy (type and ID as string)
        actual_discoveries = {
            (call.kwargs["device_type"], str(call.kwargs["device_id"]))
            for call in spy_discovery.call_args_list
        }

        # Build expected discoveries from the JSON file content
        expected_discoveries = {("plant", plant_id)}

        def extract_expected(devices, is_v3_api):
            # According to requirement: in V3, type 1 is plant, type 2 is DTU.
            dtu_type = 2 if is_v3_api else 1
            for dev in devices:
                dev_type = dev.get("type")
                dev_id = str(dev.get("id"))

                if dev_type == dtu_type:
                    expected_discoveries.add(("dtu", dev_id))
                elif dev_type in (3, 6):
                    expected_discoveries.add(("micro", dev_id))
                elif dev_type == 10:
                    expected_discoveries.add(("bms", dev_id))

                # Always check children recursively
                children = dev.get("children", [])
                if children:
                    extract_expected(children, is_v3_api)

        if mock_hw_data:
            extract_expected(mock_hw_data, is_v3)

        # Strict comparison of IDs and types detected vs JSON expectations
        assert actual_discoveries == expected_discoveries

        # 5. Verify internal cache contents match the JSON expectations
        expected_micros = {d[1] for d in expected_discoveries if d[0] == "micro"}
        expected_bms = {d[1] for d in expected_discoveries if d[0] == "bms"}

        assert app_instance.micro_ids_by_plant[plant_id] == expected_micros
        assert app_instance.bms_ids_by_plant[plant_id] == expected_bms
