"""Тесты для файловых менеджеров самолетов (JSON/CSV/TXT)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from managment import CSVSaver, FileManagerAbstract, JSONSaver, TXTSaver
from work_with_plane import Aeroplane


@pytest.fixture()
def aeroplane() -> Aeroplane:
    return Aeroplane("UAL1621", "United States", 268.79, 10203.18)


@pytest.fixture()
def another_aeroplane() -> Aeroplane:
    return Aeroplane("IBE3162", "Spain", 245.3, 10668.0)


class TestAbstractness:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            FileManagerAbstract()  # type: ignore[abstract]

    def test_abstract_methods_have_no_implementation(self) -> None:
        expected = {"_ensure_storage", "_read_records", "_write_records"}
        assert expected.issubset(FileManagerAbstract.__abstractmethods__)


class TestJSONSaver:
    def test_default_filename(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        saver = JSONSaver()
        assert saver.filename == "data_plane.json"
        assert Path("data_plane.json").exists()

    def test_custom_filename_stored_privately(self, tmp_path: Path) -> None:
        custom = str(tmp_path / "planes.json")
        saver = JSONSaver(custom)
        assert saver.filename == custom
        assert hasattr(saver, "_FileManagerAbstract__filename")
        assert not hasattr(saver, "filename_attr_public")

    def test_filename_is_read_only_property(self, tmp_path: Path) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        with pytest.raises(AttributeError):
            saver.filename = "other.json"  # type: ignore[misc]

    def test_file_initialized_as_empty_list(self, tmp_path: Path) -> None:
        path = tmp_path / "planes.json"
        JSONSaver(str(path))
        assert json.loads(path.read_text(encoding="utf-8")) == []

    def test_add_writes_list_of_dicts(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        path = tmp_path / "planes.json"
        saver = JSONSaver(str(path))
        assert saver.add_aeroplane(aeroplane) is True
        assert saver.add_aeroplane(another_aeroplane) is True

        records = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(records, list)
        assert all(isinstance(r, dict) for r in records)
        assert len(records) == 2
        assert records[0] == aeroplane.to_dict()

    def test_add_rejects_duplicates(self, tmp_path: Path, aeroplane: Aeroplane) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        assert saver.add_aeroplane(aeroplane) is True
        assert saver.add_aeroplane(aeroplane) is False
        assert len(saver.get_data()) == 1

    def test_add_rejects_non_aeroplane(self, tmp_path: Path) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        with pytest.raises(TypeError):
            saver.add_aeroplane("not a plane")  # type: ignore[arg-type]

    def test_add_rejects_invalid_aeroplane(self, tmp_path: Path) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        with pytest.raises(ValueError):
            saver.add_aeroplane(Aeroplane("", "", 0, 0))

    def test_file_persists_between_instances(
        self, tmp_path: Path, aeroplane: Aeroplane
    ) -> None:
        path = tmp_path / "planes.json"
        JSONSaver(str(path)).add_aeroplane(aeroplane)
        second = JSONSaver(str(path))
        assert len(second.get_data()) == 1
        assert second.get_data()[0] == aeroplane

    def test_get_data_with_criteria(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        saver.add_aeroplane(another_aeroplane)

        found = saver.get_data(origin_country="Spain")
        assert [plane.callsign for plane in found] == ["IBE3162"]

    def test_get_data_returns_all_without_criteria(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        saver.add_aeroplane(another_aeroplane)
        assert len(saver.get_data()) == 2

    def test_get_data_with_unknown_field_returns_empty(
        self, tmp_path: Path, aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        assert saver.get_data(unknown_field="anything") == []

    def test_delete_by_object(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        saver.add_aeroplane(another_aeroplane)

        assert saver.delete_aeroplane(aeroplane) == 1
        remaining = saver.get_data()
        assert len(remaining) == 1
        assert remaining[0] == another_aeroplane

    def test_delete_by_criteria(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        saver.add_aeroplane(another_aeroplane)

        assert saver.delete_aeroplane(origin_country="Spain") == 1
        assert saver.get_data()[0].origin_country == "United States"

    def test_delete_without_params_returns_zero(
        self, tmp_path: Path, aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        assert saver.delete_aeroplane() == 0
        assert len(saver.get_data()) == 1

    def test_delete_when_nothing_matches(
        self, tmp_path: Path, aeroplane: Aeroplane
    ) -> None:
        saver = JSONSaver(str(tmp_path / "planes.json"))
        saver.add_aeroplane(aeroplane)
        assert saver.delete_aeroplane(callsign="MISSING") == 0
        assert len(saver.get_data()) == 1

    def test_read_corrupted_file_returns_empty(self, tmp_path: Path) -> None:
        path = tmp_path / "planes.json"
        path.write_text("not a valid json", encoding="utf-8")
        saver = JSONSaver(str(path))
        assert saver.get_data() == []

    def test_read_when_json_is_not_list(self, tmp_path: Path) -> None:
        path = tmp_path / "planes.json"
        path.write_text('{"a": 1}', encoding="utf-8")
        saver = JSONSaver(str(path))
        assert saver.get_data() == []


class TestCSVSaver:
    def test_creates_file_with_header(self, tmp_path: Path) -> None:
        path = tmp_path / "planes.csv"
        CSVSaver(str(path))
        assert path.exists()
        header = path.read_text(encoding="utf-8").splitlines()[0]
        assert "callsign" in header

    def test_add_and_read_back(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = CSVSaver(str(tmp_path / "planes.csv"))
        assert saver.add_aeroplane(aeroplane) is True
        assert saver.add_aeroplane(another_aeroplane) is True
        assert saver.add_aeroplane(aeroplane) is False

        planes = saver.get_data()
        assert len(planes) == 2
        assert {p.callsign for p in planes} == {"UAL1621", "IBE3162"}

    def test_delete_by_object(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = CSVSaver(str(tmp_path / "planes.csv"))
        saver.add_aeroplane(aeroplane)
        saver.add_aeroplane(another_aeroplane)
        assert saver.delete_aeroplane(another_aeroplane) == 1

    def test_rejects_non_aeroplane(self, tmp_path: Path) -> None:
        saver = CSVSaver(str(tmp_path / "planes.csv"))
        with pytest.raises(TypeError):
            saver.add_aeroplane({"not": "a plane"})  # type: ignore[arg-type]


class TestTXTSaver:
    def test_creates_empty_file(self, tmp_path: Path) -> None:
        path = tmp_path / "planes.txt"
        TXTSaver(str(path))
        assert path.exists()
        assert path.read_text(encoding="utf-8") == ""

    def test_add_and_read_back(self, tmp_path: Path, aeroplane: Aeroplane) -> None:
        saver = TXTSaver(str(tmp_path / "planes.txt"))
        assert saver.add_aeroplane(aeroplane) is True
        planes = saver.get_data()
        assert len(planes) == 1
        assert planes[0] == aeroplane

    def test_no_duplicates(self, tmp_path: Path, aeroplane: Aeroplane) -> None:
        saver = TXTSaver(str(tmp_path / "planes.txt"))
        saver.add_aeroplane(aeroplane)
        assert saver.add_aeroplane(aeroplane) is False
        assert len(saver.get_data()) == 1

    def test_delete_by_criteria(
        self, tmp_path: Path, aeroplane: Aeroplane, another_aeroplane: Aeroplane
    ) -> None:
        saver = TXTSaver(str(tmp_path / "planes.txt"))
        saver.add_aeroplane(aeroplane)
        saver.add_aeroplane(another_aeroplane)
        assert saver.delete_aeroplane(callsign="UAL1621") == 1
        remaining = saver.get_data()
        assert len(remaining) == 1
        assert remaining[0].callsign == "IBE3162"

    def test_skips_blank_lines_when_reading(
        self, tmp_path: Path, aeroplane: Aeroplane
    ) -> None:
        path = tmp_path / "planes.txt"
        saver = TXTSaver(str(path))
        saver.add_aeroplane(aeroplane)
        path.write_text(path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
        assert len(saver.get_data()) == 1
