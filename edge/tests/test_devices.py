import os

import pytest
import yaml
from hoymiles.api_schema.station_select_device_of_tree import DeviceTree
from hoymiles.devices import BMS, Dtu, Micros, PlantObject

file_list = [("1.json"), ("2.json"), ("3.json"), ("3v1.json")]

base_path = os.path.join(
    os.path.dirname(__file__), "resp_data", "station_select_device_of_tree"
)


class TestPlantObject:
    # @pytest.mark.parametrize("file_name", [("1.json"), ("2.json"), ("3.json")])
    # def test_data_find_schema(self, file_name: str):
    #     """Test is checking if schema is correctly parsing json data for station_select_device_of_tree endpoint

    #     :param file_name: file name with json data
    #     :type file_name: str
    #     """
    #     file_path = os.path.join(
    #         base_path, "station_select_device_of_tree", file_name
    #     )
    #     with open(file_path, "r") as file:
    #         data = yaml.safe_load(file)
    #         dev_tree = DeviceTree.model_validate(dict(data))
    #         for dev in dev_tree.data:
    #             if dev.type == 1:
    #                 assert isinstance(PlantObject(dev), PlantObject)
    #             elif dev.type == 2:
    #                 assert isinstance(Micros(dev), PlantObject)
    #             elif dev.type == 3:
    #                 assert isinstance(BMS(dev), PlantObject)
    #             else:
    #                 assert False

    @pytest.mark.parametrize("file_name", file_list)
    def test_plant_obj_creation_with_validation(self, file_name: str):
        """Test is checking if PlantObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """
        if "3v" in file_name:
            pytest.skip(f"Skipping validation for v3 file: {file_name}")
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            dev_tree = DeviceTree.model_validate(dict(data))

            for dev in dev_tree.data:
                assert isinstance(PlantObject(dev), PlantObject)
                if dev.children:
                    for child in dev.children:
                        assert isinstance(PlantObject(child), PlantObject)
                        if child.children:
                            for sub_child in child.children:
                                assert isinstance(PlantObject(sub_child), PlantObject)

    @pytest.mark.parametrize("file_name", file_list)
    def test_plant_obj_creation_without_validation(self, file_name: str):
        """Test is checking if PlantObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data: dict = yaml.safe_load(file)

            for dev in data.get("data"):
                test_obj = PlantObject(dev)
                assert isinstance(test_obj, PlantObject)
                if dev.get("children"):
                    for child in dev.get("children"):
                        test_obj = PlantObject(child)
                        assert isinstance(test_obj, PlantObject)
                        if child.get("children"):
                            test_obj = PlantObject(child)
                            for sub_child in child.get("children"):
                                assert isinstance(test_obj, PlantObject)

        print("dupasa")


class TestDtu:
    @pytest.mark.parametrize("file_name", file_list)
    def test_dtu_creation(self, file_name: str):
        """Test is checking if DtuObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """
        if "3v" in file_name:
            pytest.skip(f"Skipping validation for v3 file: {file_name}")
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            dev_tree = DeviceTree.model_validate(dict(data))
            for dev in dev_tree.data:
                assert isinstance(Dtu(dev), Dtu)
                if dev.children:
                    for child in dev.children:
                        assert isinstance(Dtu(child), Dtu)
                        if child.children:
                            for sub_child in child.children:
                                assert isinstance(Dtu(sub_child), Dtu)

    @pytest.mark.parametrize("file_name", file_list)
    def test_dtu_creation_without_validation(self, file_name: str):
        """Test is checking if DtuObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """

        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            for dev in data.get("data"):
                assert isinstance(Dtu(dev), Dtu)
                if dev.get("children"):
                    for child in dev.get("children"):
                        assert isinstance(Dtu(child), Dtu)
                        if child.get("children"):
                            for sub_child in child.get("children"):
                                assert isinstance(Dtu(sub_child), Dtu)


class TestMicros:
    @pytest.mark.parametrize("file_name", file_list)
    def test_micros_obj_creation(self, file_name: str):
        """Test is checking if MicrosObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """
        if "3v" in file_name:
            pytest.skip(f"Skipping validation for v3 file: {file_name}")
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            dev_tree = DeviceTree.model_validate(dict(data))
            for dev in dev_tree.data:
                assert isinstance(Micros(dev), Micros)
                if dev.children:
                    for child in dev.children:
                        assert isinstance(Micros(child), Micros)
                        if child.children:
                            for sub_child in child.children:
                                assert isinstance(Micros(sub_child), Micros)

    @pytest.mark.parametrize("file_name", file_list)
    def test_micros_obj_creation_without_validation(self, file_name: str):
        """Test is checking if MicrosObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """

        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            for dev in data.get("data"):
                assert isinstance(Micros(dev), Micros)
                if dev.get("children"):
                    for child in dev.get("children"):
                        assert isinstance(Micros(child), Micros)
                        if child.get("children"):
                            for sub_child in child.get("children"):
                                assert isinstance(Micros(sub_child), Micros)


class TestBMS:
    @pytest.mark.parametrize("file_name", file_list)
    def test_bms_obj_creation(self, file_name: str):
        """Test is checking if BMSObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """
        if "3v" in file_name:
            pytest.skip(f"Skipping validation for v3 file: {file_name}")
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            dev_tree = DeviceTree.model_validate(dict(data))
            for dev in dev_tree.data:
                assert isinstance(BMS(dev), BMS)
                if dev.children:
                    for child in dev.children:
                        assert isinstance(BMS(child), BMS)
                        if child.children:
                            for sub_child in child.children:
                                assert isinstance(BMS(sub_child), BMS)

    @pytest.mark.parametrize("file_name", file_list)
    def test_bms_obj_creation_without_validation(self, file_name: str):
        """Test is checking if BMSObject could be created from DeviceTree data

        :param file_name: file name with json data
        :type file_name: str
        """
        file_path = os.path.join(base_path, file_name)
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            for dev in data.get("data"):
                assert isinstance(BMS(dev), BMS)
                if dev.get("children"):
                    for child in dev.get("children"):
                        assert isinstance(BMS(child), BMS)
                        if child.get("children"):
                            for sub_child in child.get("children"):
                                assert isinstance(BMS(sub_child), BMS)
