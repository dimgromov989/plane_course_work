"""Тесты для AeroplanesAPI (с моком requests)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from base_plane import AbstractPlaneBase
from plane_info import AeroplanesAPI


def _mock_response(status_code: int, payload: Any) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


class TestAbstractPlaneBase:
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            AbstractPlaneBase()  # type: ignore[abstract]


class TestAeroplanesAPI:
    def test_init_sets_urls_from_parent(self) -> None:
        api = AeroplanesAPI()
        assert api._openstreetmap_url == "https://nominatim.openstreetmap.org/search"
        assert api._opensky_url == "https://opensky-network.org/api/states/all"
        assert api._aeroplanes is None

    def test_connection_api_success(self) -> None:
        api = AeroplanesAPI()
        with patch("plane_info.requests.get", return_value=_mock_response(200, {"ok": 1})) as mocked:
            result = api._connection_api("https://example.com", {"q": "x"})
        assert result == {"ok": 1}
        mocked.assert_called_once()

    def test_connection_api_non_200_raises(self) -> None:
        api = AeroplanesAPI()
        with patch("plane_info.requests.get", return_value=_mock_response(500, {})):
            with pytest.raises(Exception, match="500"):
                api._connection_api("https://example.com", {})

    def test_get_aeroplanes_happy_path(self) -> None:
        api = AeroplanesAPI()
        coords_response = [{"boundingbox": ["1", "2", "3", "4"]}]
        states_response = {"states": [[None, "ABC", "Spain"] + [None] * 14]}

        call_results = iter([coords_response, states_response])
        with patch.object(api, "_connection_api", side_effect=lambda *a, **k: next(call_results)) as mocked:
            result = api.get_aeroplanes("Spain")

        assert result == states_response
        assert mocked.call_count == 2

    def test_get_aeroplanes_when_country_not_found(self) -> None:
        api = AeroplanesAPI()
        with patch.object(api, "_connection_api", return_value=[]):
            with pytest.raises(ValueError, match="Narnia"):
                api.get_aeroplanes("Narnia")

    def test_save_aeroplanes_writes_valid_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        api = AeroplanesAPI()
        payload = {"states": [[None, "ABC"]]}
        api.save_aeroplanes(payload)
        saved = json.loads((tmp_path / "data_plane.json").read_text(encoding="utf-8"))
        assert saved == payload
