"""Тесты для функций пользовательского взаимодействия."""
from __future__ import annotations

import pytest

from user_interaction import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)
from work_with_plane import Aeroplane


@pytest.fixture()
def planes() -> list[Aeroplane]:
    return [
        Aeroplane("AAA", "Spain", 200.0, 1000.0),
        Aeroplane("BBB", "Germany", 250.0, 5000.0),
        Aeroplane("CCC", "France", 300.0, 10000.0),
        Aeroplane("DDD", "United States", 150.0, 7000.0),
        Aeroplane("EEE", "Spain", 280.0, 12000.0),
    ]


class TestFilterAeroplanes:
    def test_exact_country_match(self, planes: list[Aeroplane]) -> None:
        result = filter_aeroplanes(planes, ["Spain"])
        assert [p.callsign for p in result] == ["AAA", "EEE"]

    def test_case_insensitive(self, planes: list[Aeroplane]) -> None:
        result = filter_aeroplanes(planes, ["spain", "GERMANY"])
        assert {p.callsign for p in result} == {"AAA", "BBB", "EEE"}

    def test_empty_filter_returns_all(self, planes: list[Aeroplane]) -> None:
        assert filter_aeroplanes(planes, []) == planes

    def test_blank_filter_strings_ignored(self, planes: list[Aeroplane]) -> None:
        assert filter_aeroplanes(planes, ["   ", ""]) == planes

    def test_no_matches_returns_empty(self, planes: list[Aeroplane]) -> None:
        assert filter_aeroplanes(planes, ["Narnia"]) == []

    def test_empty_input_list(self) -> None:
        assert filter_aeroplanes([], ["Spain"]) == []

    def test_handles_exception_and_returns_empty(self) -> None:
        class Broken:
            @property
            def origin_country(self) -> str:
                raise RuntimeError("boom")

        assert filter_aeroplanes([Broken()], ["Spain"]) == []  # type: ignore[list-item]


class TestGetAeroplanesByAltitude:
    def test_filters_by_range(self, planes: list[Aeroplane]) -> None:
        result = get_aeroplanes_by_altitude(planes, (4000.0, 10000.0))
        assert {p.callsign for p in result} == {"BBB", "CCC", "DDD"}

    def test_inclusive_boundaries(self, planes: list[Aeroplane]) -> None:
        result = get_aeroplanes_by_altitude(planes, (1000.0, 1000.0))
        assert [p.callsign for p in result] == ["AAA"]

    def test_empty_range_returns_empty(self, planes: list[Aeroplane]) -> None:
        assert get_aeroplanes_by_altitude(planes, (100000.0, 200000.0)) == []

    def test_handles_exception_gracefully(self, planes: list[Aeroplane]) -> None:
        assert get_aeroplanes_by_altitude(planes, "broken") == []  # type: ignore[arg-type]


class TestSortAeroplanes:
    def test_sorts_by_altitude_ascending(self, planes: list[Aeroplane]) -> None:
        result = sort_aeroplanes(planes)
        assert [p.callsign for p in result] == ["AAA", "BBB", "DDD", "CCC", "EEE"]

    def test_empty_list(self) -> None:
        assert sort_aeroplanes([]) == []

    def test_handles_exception_gracefully(self) -> None:
        assert sort_aeroplanes("not a list") == []  # type: ignore[arg-type]


class TestGetTopAeroplanes:
    def test_returns_first_n(self, planes: list[Aeroplane]) -> None:
        top = get_top_aeroplanes(planes, 2)
        assert len(top) == 2
        assert top[0].callsign == "AAA"

    def test_n_larger_than_list_returns_all(self, planes: list[Aeroplane]) -> None:
        assert get_top_aeroplanes(planes, 100) == planes

    def test_n_zero_returns_empty(self, planes: list[Aeroplane]) -> None:
        assert get_top_aeroplanes(planes, 0) == []

    def test_handles_exception_gracefully(self) -> None:
        assert get_top_aeroplanes(None, 3) == []  # type: ignore[arg-type]


class TestPrintAeroplanes:
    def test_prints_each_plane(
        self, planes: list[Aeroplane], capsys: pytest.CaptureFixture[str]
    ) -> None:
        print_aeroplanes(planes[:2])
        captured = capsys.readouterr().out
        assert "AAA" in captured
        assert "BBB" in captured

    def test_empty_list_prints_nothing(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        print_aeroplanes([])
        assert capsys.readouterr().out == ""

    def test_handles_exception_gracefully(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        print_aeroplanes(None)  # type: ignore[arg-type]
        assert "Ошибка" in capsys.readouterr().out
