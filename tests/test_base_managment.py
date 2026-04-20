"""Тесты для реэкспорта абстракции в base_managment.py."""
from __future__ import annotations

from base_managment import FileManagerAbstract, JsonSaverAbstract
from managment import FileManagerAbstract as OriginalFileManager


def test_reexports_point_to_original_class() -> None:
    assert FileManagerAbstract is OriginalFileManager
    assert JsonSaverAbstract is OriginalFileManager
