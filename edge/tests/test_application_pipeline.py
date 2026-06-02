import os

import pytest
import yaml

# Path to response data files, relative to the project root
BASE_PATH = os.path.join(
    os.path.dirname(__file__), "resp_data", "data_count_station_real_data"
)


class TestApplicationPipeline:
    """Tests for the data transformation pipeline in HoymilesApplication."""

    @pytest.mark.parametrize(
        "file_name", ["1.json", "2.json", "3.json", "4.json", "5.json", "3v1.json"]
    )
    def test_plant_pipeline_execution(self, app_instance, file_name):
        """
        Test self.plant_pipeline.execute(solar_data) using sample JSON data.

        This verifies that the pipeline correctly applies transformations like:
        - Calculating kW values (real_power_kw, array_size_kW)
        - Casting fields to float
        - Rounding numeric values
        - Filtering out null values
        """
        file_path = os.path.join(BASE_PATH, file_name)
        with open(file_path, "r") as f:
            raw_response = yaml.safe_load(f)
            # The pipeline processes the 'data' field returned by CloudApi.get_solar_data
            solar_data = raw_response.get("data", {})

        # Execute the transformation pipeline
        transformed = app_instance.plant_pipeline.execute(solar_data)

        # 1. Verify Calculated Fields
        if "real_power" in solar_data and solar_data["real_power"] is not None:
            assert "real_power_kw" in transformed
            # Value check: (int(raw_value) / 1000) rounded to 3 decimal places
            expected_kw = round(float(solar_data.get("real_power", 0)) / 1000, 3)
            assert transformed["real_power_kw"] == expected_kw

        if "array_size" in solar_data and solar_data["array_size"] is not None:
            assert "array_size_kW" in transformed
            expected_array_kw = round(int(solar_data.get("array_size", 0)) / 1000, 3)
            assert transformed["array_size_kW"] == expected_array_kw

        # 2. Verify Type Casting (Casting to float per pipeline definition)
        for float_key in ["real_power", "today_eq", "month_eq", "total_eq"]:
            if float_key in transformed:
                assert isinstance(transformed[float_key], float)

        # 3. Verify Null Filtering (FilterNullTransformer)
        for key, value in transformed.items():
            assert value is not None, (
                f"Value for key '{key}' should not be None after pipeline execution"
            )
            assert value != "", f"Value for key '{key}' should not be an empty string"

    def test_extract_bms_payload(self, app_instance):
        """Test BMS data extraction from solar response."""
        solar_data = {"reflux_station_data": {"bms_soc": 45, "bms_power": 1}}
        payload = app_instance._extract_bms_payload_from_solar_data(solar_data)
        assert payload["reserve_soc"] == 45
        assert payload["connect"] is True

        assert app_instance._extract_bms_payload_from_solar_data({}) == {}
