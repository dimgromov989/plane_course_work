
class Aeroplane:
    """Класс для работы с самолетом"""
    __slots__ = ('callsign', 'origin_country', 'velocity', 'baro_altitude', '_raw_state')

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity: float,
        baro_altitude: float,
        raw_state: list | None = None,
    ):
        self.callsign = (callsign or '').strip()
        self.origin_country = (origin_country or '').strip()
        self.velocity = self._to_float(velocity)
        self.baro_altitude = self._to_float(baro_altitude)
        self._raw_state = list(raw_state) if isinstance(raw_state, list) else None

    @staticmethod
    def _to_float(value: float | int | None) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _valid_data(self) -> bool:
        """Метод для валидации данных"""
        return bool(self.callsign and self.origin_country)

    def to_dict(self) -> dict:
        """Преобразование объекта самолета в словарь"""
        return {
            'callsign': self.callsign,
            'origin_country': self.origin_country,
            'velocity': self.velocity,
            'baro_altitude': self.baro_altitude,
        }

    def to_state(self) -> list:
        """Преобразование объекта самолета в формат OpenSky states"""
        if self._raw_state is not None:
            state = list(self._raw_state)
            while len(state) < 17:
                state.append(None)
        else:
            state = [None] * 17
            state[8] = False
            state[15] = False
            state[16] = 0

        state[1] = self.callsign
        state[2] = self.origin_country
        state[7] = self.baro_altitude
        state[9] = self.velocity
        state[13] = self.baro_altitude
        return state

    @classmethod
    def from_dict(cls, data: dict) -> 'Aeroplane':
        """Создание объекта самолета из словаря"""
        return cls(
            data.get('callsign', ''),
            data.get('origin_country', ''),
            data.get('velocity', 0.0),
            data.get('baro_altitude', 0.0),
        )

    @classmethod
    def cast_to_object_list(cls, data: dict | list | None) -> list['Aeroplane']:
        """Преобразует ответ OpenSky (dict со states или список) в список объектов."""
        if data is None:
            return []
        states = data.get('states') if isinstance(data, dict) else data
        if not states:
            return []
        return [cls.from_state(state) for state in states if isinstance(state, list)]

    @classmethod
    def from_state(cls, state: list) -> 'Aeroplane':
        """Создание объекта самолета из ответа OpenSky states"""
        baro_altitude = state[7] if len(state) > 7 and state[7] is not None else 0.0
        if baro_altitude == 0.0 and len(state) > 13 and state[13] is not None:
            baro_altitude = state[13]

        return cls(
            state[1] if len(state) > 1 else '',
            state[2] if len(state) > 2 else '',
            state[9] if len(state) > 9 else 0.0,
            baro_altitude,
            state,
        )

    def __repr__(self) -> str:
        """Удобное строковое представление объекта"""
        return (
            f"Aeroplane(callsign='{self.callsign}', "
            f"origin_country='{self.origin_country}', "
            f"velocity={self.velocity}, "
            f"baro_altitude={self.baro_altitude})"
        )

    def __eq__(self, other: 'Aeroplane') -> bool:
        """Метод для сравнения самолетов по всем атрибутам"""
        if not isinstance(other, Aeroplane):
            return False
        return (
            self.callsign == other.callsign
            and self.origin_country == other.origin_country
            and self.velocity == other.velocity
            and self.baro_altitude == other.baro_altitude
        )
        






