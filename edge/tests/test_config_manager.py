import json

import pytest
from hoymiles.config_manager import ConfigError, ConfigManager


def test_config_manager_defaults():
    config = ConfigManager()
    assert config.get("LOG_LEVEL") == "INFO"
    assert config.get_int("GET_DATA_INTERVAL") == 480
    assert config.get_bool("USE_ESTAR") is False


def test_config_manager_load_from_dict():
    config = ConfigManager()
    config.load_from_dict({"HOYMILES_USER": "test@user.com"})
    assert config.get("HOYMILES_USER") == "test@user.com"


def test_config_manager_get_types():
    config = ConfigManager()
    config.set("INT_VAL", "100")
    config.set("BOOL_VAL", "true")
    config.set("BOOL_VAL_OFF", "0")
    assert config.get_int("INT_VAL") == 100
    assert config.get_bool("BOOL_VAL") is True
    assert config.get_bool("BOOL_VAL_OFF") is False
    assert config.get_str("INT_VAL") == "100"


def test_config_manager_get_list():
    config = ConfigManager()
    config.set("PLANTS", "123,456:789")
    assert config.get_list("PLANTS") == ["123", "456", "789"]
    config.set("PLANTS_LIST", ["a", "b"])
    assert config.get_list("PLANTS_LIST") == ["a", "b"]


def test_config_manager_validate_missing():
    config = ConfigManager()
    with pytest.raises(ConfigError, match="Missing required configuration"):
        config.validate()


def test_config_manager_validate_success():
    config = ConfigManager()
    config.load_from_dict(
        {
            "HOYMILES_USER": "u",
            "HOYMILES_PASSWORD": "p",
            "HOYMILES_PLANT_ID": "id",
            "MQTT_HOST": "h",
            "MQTT_USER": "u",
            "MQTT_PASS": "p",
        }
    )
    assert config.validate() is True


def test_config_manager_load_from_env(monkeypatch):
    monkeypatch.setenv("HOYMILES_USER", "env_user")
    monkeypatch.setenv("GET_DATA_INTERVAL", "600")
    config = ConfigManager()
    config.load_from_env()
    assert config.get("HOYMILES_USER") == "env_user"
    assert config.get_int("GET_DATA_INTERVAL") == 600


def test_config_manager_load_from_file(tmp_path):
    config_file = tmp_path / "config.json"
    data = {"options": {"HOYMILES_USER": "file_user"}}
    config_file.write_text(json.dumps(data))

    config = ConfigManager()
    config.load_from_file(str(config_file))
    assert config.get("HOYMILES_USER") == "file_user"


def test_config_manager_reset():
    config = ConfigManager()
    config.set("LOG_LEVEL", "DEBUG")
    config.reset_to_defaults()
    assert config.get("LOG_LEVEL") == "INFO"
