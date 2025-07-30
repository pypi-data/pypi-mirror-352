import json
import pytest

from src.lunar_policy import Check, ComponentData


class TestCheckGet:
    def test_get_valid_path(self):
        data = ComponentData.from_component_json(json.dumps({
            "hi": "there"
        }))

        with Check("test", data=data) as c:
            c.get(".hi")

    def test_get_invalid_path(self):
        data = ComponentData.from_component_json("{}")

        with pytest.raises(ValueError):
            with Check("test", data=data) as c:
                c.get("@#$@#$@#$")

    def test_get_or_default(self):
        data = ComponentData.from_component_json(json.dumps({
            "hi": "there"
        }))

        exists, default = "", ""
        with Check("test", data=data) as c:
            exists = c.get_or_default(".hi", "default")
            default = c.get_or_default(".not.a.path", "default")

        assert exists == "there"
        assert default == "default"

    def test_get_all_valid_path_single(self):
        data = ComponentData.from_json(json.dumps({
            "merged_blob": {},
            "metadata_instances": [
                {
                    "payload": {
                        "hi": "there"
                    }
                }
            ]
        }))

        all = []
        with Check("test", data=data) as c:
            all = c.get_all(".hi")

        assert all == ["there"]

    def test_get_all_valid_path_multiple(self):
        data = ComponentData.from_json(json.dumps({
            "merged_blob": {},
            "metadata_instances": [
                {
                    "payload": {
                        "hi": "there"
                    }
                },
                {
                    "payload": {
                        "hi": "there"
                    }
                }
            ]
        }))

        all = []
        with Check("test", data=data) as c:
            all = c.get_all(".hi")

        assert all == ["there", "there"]

    def test_get_all_invalid_path(self):
        data = ComponentData.from_component_json("{}")

        with pytest.raises(ValueError):
            with Check("test", data=data) as c:
                c.get_all("@#$@#$@#$")

    def test_get_all_or_default(self):
        data = ComponentData.from_json(json.dumps({
            "merged_blob": {},
            "metadata_instances": [
                {
                    "payload": {
                        "hi": "there"
                    }
                }
            ]
        }))

        exists, default = "", ""
        with Check("test", data=data) as c:
            exists = c.get_all_or_default(".hi", "default")
            default = c.get_all_or_default(".not.a.path", "default")

        assert exists == ["there"]
        assert default == ["default"]
