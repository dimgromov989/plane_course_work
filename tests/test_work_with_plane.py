"""Тесты для класса Aeroplane."""
from __future__ import annotations

import pytest

from work_with_plane import Aeroplane


@pytest.fixture()
def aeroplane() -> Aeroplane:
    return Aeroplane("UAL1621", "United States", 268.79, 10203.18)


class TestAeroplaneInit:
    def test_basic_fields_stored(self, aeroplane: Aeroplane) -> None:
        assert aeroplane.callsign == "UAL1621"
        assert aeroplane.origin_country == "United States"
        assert aeroplane.velocity == 268.79
        assert aeroplane.baro_altitude == 10203.18

    def test_strips_whitespace(self) -> None:
        plane = Aeroplane("  ABC  ", "  Germany  ", 0, 0)
        assert plane.callsign == "ABC"
        assert plane.origin_country == "Germany"

    def test_handles_none_strings(self) -> None:
        plane = Aeroplane(None, None, None, None)  # type: ignore[arg-type]
        assert plane.callsign == ""
        assert plane.origin_country == ""
        assert plane.velocity == 0.0
        assert plane.baro_altitude == 0.0

    def test_to_float_with_invalid_values(self) -> None:
        plane = Aeroplane("X", "Y", "not-a-number", [1, 2])  # type: ignore[arg-type]
        assert plane.velocity == 0.0
        assert plane.baro_altitude == 0.0


class TestValidData:
    def test_valid_when_fields_filled(self, aeroplane: Aeroplane) -> None:
        assert aeroplane._valid_data() is True

    @pytest.mark.parametrize(
        "callsign,country",
        [("", "Germany"), ("ABC", ""), ("", ""), ("   ", "Germany")],
    )
    def test_invalid_when_missing_fields(self, callsign: str, country: str) -> None:
        assert Aeroplane(callsign, country, 1, 1)._valid_data() is False


class TestSerialization:
    def test_to_dict(self, aeroplane: Aeroplane) -> None:
        assert aeroplane.to_dict() == {
            "callsign": "UAL1621",
            "origin_country": "United States",
            "velocity": 268.79,
            "baro_altitude": 10203.18,
        }

    def test_from_dict_roundtrip(self, aeroplane: Aeroplane) -> None:
        restored = Aeroplane.from_dict(aeroplane.to_dict())
        assert restored == aeroplane

    def test_from_dict_with_missing_keys_uses_defaults(self) -> None:
        plane = Aeroplane.from_dict({})
        assert plane.callsign == ""
        assert plane.origin_country == ""
        assert plane.velocity == 0.0
        assert plane.baro_altitude == 0.0


class TestStateConversion:
    def test_from_state_happy_path(self) -> None:
        state = [None] * 17
        state[1] = "ABC123"
        state[2] = "Spain"
        state[7] = 9000.0
        state[9] = 230.5
        plane = Aeroplane.from_state(state)
        assert plane.callsign == "ABC123"
        assert plane.origin_country == "Spain"
        assert plane.baro_altitude == 9000.0
        assert plane.velocity == 230.5

    def test_from_state_falls_back_to_geo_altitude(self) -> None:
        state = [None] * 17
        state[1] = "ABC"
        state[2] = "Spain"
        state[7] = None
        state[9] = 100.0
        state[13] = 5000.0
        plane = Aeroplane.from_state(state)
        assert plane.baro_altitude == 5000.0

    def test_from_state_short_list(self) -> None:
        plane = Aeroplane.from_state([])
        assert plane.callsign == ""
        assert plane.origin_country == ""

    def test_to_state_roundtrip_preserves_raw(self) -> None:
        state = [None] * 17
        state[0] = "icao24"
        state[1] = "ABC"
        state[2] = "Spain"
        state[7] = 9000.0
        state[9] = 230.5
        plane = Aeroplane.from_state(state)
        rebuilt = plane.to_state()
        assert rebuilt[0] == "icao24"
        assert rebuilt[1] == "ABC"
        assert rebuilt[2] == "Spain"
        assert rebuilt[9] == 230.5

    def test_to_state_when_raw_missing(self) -> None:
        plane = Aeroplane("X", "Y", 1.0, 2.0)
        state = plane.to_state()
        assert len(state) == 17
        assert state[1] == "X"
        assert state[2] == "Y"
        assert state[9] == 1.0
        assert state[7] == 2.0


class TestCastToObjectList:
    def test_from_opensky_dict(self) -> None:
        response = {
            "time": 123,
            "states": [
                [None, "ABC", "Spain", None, None, None, None, 9000.0, None, 200.0] + [None] * 7,
                [None, "DEF", "Germany", None, None, None, None, 8000.0, None, 210.0] + [None] * 7,
            ],
        }
        planes = Aeroplane.cast_to_object_list(response)
        assert len(planes) == 2
        assert planes[0].callsign == "ABC"
        assert planes[1].origin_country == "Germany"

    def test_accepts_plain_list(self) -> None:
        state = [None] * 17
        state[1] = "ABC"
        state[2] = "Spain"
        planes = Aeroplane.cast_to_object_list([state])
        assert len(planes) == 1
        assert planes[0].callsign == "ABC"

    def test_none_and_empty_return_empty_list(self) -> None:
        assert Aeroplane.cast_to_object_list(None) == []
        assert Aeroplane.cast_to_object_list({"states": None}) == []
        assert Aeroplane.cast_to_object_list([]) == []

    def test_skips_non_list_state_items(self) -> None:
        planes = Aeroplane.cast_to_object_list({"states": ["not a list", None]})
        assert planes == []


class TestEqAndRepr:
    def test_equal_when_fields_match(self, aeroplane: Aeroplane) -> None:
        twin = Aeroplane("UAL1621", "United States", 268.79, 10203.18)
        assert aeroplane == twin

    def test_not_equal_with_different_type(self, aeroplane: Aeroplane) -> None:
        assert (aeroplane == "not an aeroplane") is False

    def test_not_equal_when_field_differs(self, aeroplane: Aeroplane) -> None:
        other = Aeroplane("UAL1621", "United States", 1.0, 10203.18)
        assert aeroplane != other

    def test_repr_contains_callsign(self, aeroplane: Aeroplane) -> None:
        assert "UAL1621" in repr(aeroplane)
        assert "United States" in repr(aeroplane)
