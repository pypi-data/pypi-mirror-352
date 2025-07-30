import json

from src.lunar_policy import Check, Path, ComponentData
from src.lunar_policy.result import NoDataError


class TestCheckNoData:
    def test_can_report_no_data(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(Path(".not.a.path"))

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no_data"
        assert ".not.a.path" in results[0]["failure_message"]
        assert results[0]["op"] == "fail"

    def test_can_report_no_data_with_get(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.get(".not.a.path")

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no_data"
        assert ".not.a.path" in results[0]["failure_message"]
        assert results[0]["op"] == "fail"

    def test_can_report_no_data_with_get_all(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.get_all(".not.a.path")

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no_data"
        assert ".not.a.path" in results[0]["failure_message"]
        assert results[0]["op"] == "fail"

    def test_assert_none_is_no_data(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.assert_true(None)

        captured = capsys.readouterr()
        results = json.loads(captured.out)["assertions"]
        assert len(results) == 1
        assert results[0]["result"] == "no_data"
        assert "None" in results[0]["failure_message"]
        assert results[0]["op"] == "fail"

    def test_exit_check_early_on_no_data(self, capsys):
        data = ComponentData.from_component_json(json.dumps({
            "value": True,
        }))

        with Check("test", data=data) as c:
            c.assert_true(Path(".value"))
            c.assert_false(Path(".not.a.path"))
            c.assert_equals("should not run", "should not run")

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 2
        assert all(a["op"] != "equals" for a in result["assertions"])

    def test_exit_check_early_on_no_data_get(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            c.get(".not.a.path")
            c.assert_equals("should not run", "should not run")

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 1

    def test_suppress_on_no_data(self, capsys):
        data = ComponentData.from_component_json("{}")
        with Check("test", data=data) as c:
            try:
                c.assert_true(Path(".not.a.path"))
            except NoDataError:
                pass

            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 1

    def test_suppress_on_no_data_get(self, capsys):
        data = ComponentData.from_component_json("{}")

        with Check("test", data=data) as c:
            try:
                c.get(".not.a.path")
            except NoDataError:
                pass

            c.assert_true(True)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["assertions"]) == 1
