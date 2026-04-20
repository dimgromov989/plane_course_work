from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from work_with_plane import Aeroplane


class FileManagerAbstract(ABC):
    """Абстрактный класс для работы с файловыми хранилищами самолетов."""

    _default_filename: str = "data_plane"

    def __init__(self, filename: str | None = None) -> None:
        self.__filename = filename or self._default_filename
        self._ensure_storage()

    @property
    def filename(self) -> str:
        """Доступ только на чтение к приватному имени файла."""
        return self.__filename

    @abstractmethod
    def _ensure_storage(self) -> None:
        """Создать пустое хранилище, если файла еще нет."""

    @abstractmethod
    def _read_records(self) -> list[dict[str, Any]]:
        """Прочитать все записи из файла."""

    @abstractmethod
    def _write_records(self, records: list[dict[str, Any]]) -> None:
        """Полностью перезаписать файл переданными записями."""

    def get_data(self, **criteria: Any) -> list[Aeroplane]:
        """Получить самолеты из файла, подходящие под критерии."""
        return [
            aeroplane
            for aeroplane in (Aeroplane.from_dict(r) for r in self._read_records())
            if self._matches(aeroplane, criteria)
        ]

    def add_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """Добавить самолет в файл, избегая дублей."""
        if not isinstance(aeroplane, Aeroplane):
            raise TypeError("Можно сохранять только объекты класса Aeroplane.")
        if not aeroplane._valid_data():
            raise ValueError("У самолета должны быть заполнены callsign и origin_country.")

        records = self._read_records()
        data = aeroplane.to_dict()
        if data in records:
            return False

        records.append(data)
        self._write_records(records)
        return True

    def delete_aeroplane(
        self,
        aeroplane: Aeroplane | None = None,
        **criteria: Any,
    ) -> int:
        """Удалить самолеты по объекту или по критериям."""
        filters = aeroplane.to_dict() if aeroplane is not None else criteria
        if not filters:
            return 0

        remaining: list[dict[str, Any]] = []
        deleted = 0
        for record in self._read_records():
            if self._matches(Aeroplane.from_dict(record), filters):
                deleted += 1
                continue
            remaining.append(record)

        if deleted:
            self._write_records(remaining)
        return deleted

    @staticmethod
    def _matches(aeroplane: Aeroplane, criteria: dict[str, Any]) -> bool:
        """Проверяет, подходит ли самолет под переданные критерии."""
        return all(
            hasattr(aeroplane, name) and getattr(aeroplane, name) == value
            for name, value in criteria.items()
        )


class JSONSaver(FileManagerAbstract):
    """Класс для работы с JSON-файлом самолетов."""

    _default_filename = "data_plane.json"

    def _ensure_storage(self) -> None:
        storage = Path(self.filename)
        if not storage.exists():
            storage.write_text("[]", encoding="utf-8")

    def _read_records(self) -> list[dict[str, Any]]:
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=4)


class CSVSaver(FileManagerAbstract):
    """Дополнительный класс для хранения данных в CSV-файле."""

    _default_filename = "data_plane.csv"
    _fieldnames = ["callsign", "origin_country", "velocity", "baro_altitude"]

    def _ensure_storage(self) -> None:
        storage = Path(self.filename)
        if not storage.exists():
            with open(self.filename, "w", encoding="utf-8", newline="") as file:
                csv.DictWriter(file, fieldnames=self._fieldnames).writeheader()

    def _read_records(self) -> list[dict[str, Any]]:
        with open(self.filename, "r", encoding="utf-8", newline="") as file:
            return [
                {
                    "callsign": row.get("callsign", ""),
                    "origin_country": row.get("origin_country", ""),
                    "velocity": float(row.get("velocity") or 0.0),
                    "baro_altitude": float(row.get("baro_altitude") or 0.0),
                }
                for row in csv.DictReader(file)
            ]

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        with open(self.filename, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._fieldnames)
            writer.writeheader()
            writer.writerows(records)


class TXTSaver(FileManagerAbstract):
    """Дополнительный класс для хранения данных в TXT-файле (построчный JSON)."""

    _default_filename = "data_plane.txt"

    def _ensure_storage(self) -> None:
        storage = Path(self.filename)
        if not storage.exists():
            storage.write_text("", encoding="utf-8")

    def _read_records(self) -> list[dict[str, Any]]:
        with open(self.filename, "r", encoding="utf-8") as file:
            return [json.loads(line) for line in file if line.strip()]

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        with open(self.filename, "w", encoding="utf-8") as file:
            file.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


JsonSaver = JSONSaver
