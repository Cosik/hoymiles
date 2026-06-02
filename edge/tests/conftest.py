import pytest
from hoymiles.application import HoymilesApplication
from hoymiles.config_manager import ConfigManager


@pytest.fixture
def app_instance(mocker):
    """Initialize HoymilesApplication with a mock configuration and mocked API calls."""
    # Mock CloudApi.get_token to prevent real authentication attempts during test setup
    mocker.patch("hoymiles.cloud_api.CloudApi.get_token", return_value=True)

    # Mock MQTT publisher to prevent real connections and network activity.
    # Patching at the class level ensures the instance created in HoymilesApplication is mocked.
    mocker.patch("hoymiles.mqtt_publisher_hass.HASS_AVAILABLE", True)
    mocker.patch(
        "hoymiles.mqtt_publisher_hass.HAMQTTPublisher.publish_discovery", return_value=0
    )
    mocker.patch(
        "hoymiles.mqtt_publisher_hass.HAMQTTPublisher.publish_data", return_value=0
    )
    mocker.patch(
        "hoymiles.mqtt_publisher_hass.HAMQTTPublisher.publish_availability",
        return_value=1,
    )
    mocker.patch(
        "hoymiles.mqtt_publisher_hass.HAMQTTPublisher.disconnect", return_value=None
    )
    mocker.patch(
        "hoymiles.mqtt_publisher_hass.HAMQTTPublisher._create_mqtt_settings",
        return_value=mocker.Mock(),
    )

    config = ConfigManager()
    config.load_from_dict(
        {
            "HOYMILES_USER": "test@example.com",
            "HOYMILES_PASSWORD": "password123",
            "HOYMILES_PLANT_ID": "12345",
            "MQTT_HOST": "localhost",
            "MQTT_USER": "user",
            "MQTT_PASS": "pass",
        }
    )
    return HoymilesApplication(config)
