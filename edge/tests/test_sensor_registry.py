from hoymiles.sensor_registry import (
    ComponentType,
    DeviceClass,
    SensorDefinition,
    SensorRegistry,
)


def test_sensor_registry_defaults():
    registry = SensorRegistry()
    assert "plant" in registry.get_device_types()
    assert "real_power" in registry.get_sensors("plant")
    assert "connect" in registry.get_sensors("dtu")


def test_sensor_registry_register():
    registry = SensorRegistry()
    new_sensor = SensorDefinition(
        key="custom_key", name="Custom Name", component_type=ComponentType.SENSOR
    )
    registry.register_sensor("custom_device", new_sensor)
    assert registry.get_sensor("custom_device", "custom_key") == new_sensor


def test_sensor_registry_get_by_component():
    registry = SensorRegistry()
    dtu_binaries = registry.get_sensors_by_component("dtu", ComponentType.BINARY_SENSOR)
    assert "connect" in dtu_binaries

    plant_numbers = registry.get_sensors_by_component("plant", ComponentType.NUMBER)
    assert len(plant_numbers) == 0


def test_sensor_definition_to_dict():
    sensor = SensorDefinition(
        key="test",
        name="Test",
        component_type=ComponentType.SENSOR,
        device_class=DeviceClass.POWER,
        unit_of_measurement="W",
    )
    d = sensor.to_dict()
    assert d["key"] == "test"
    assert d["component_type"] == "sensor"
    assert d["device_class"] == "power"
    assert d["unit_of_measurement"] == "W"
