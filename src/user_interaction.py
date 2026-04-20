from work_with_plane import Aeroplane





def filter_aeroplanes(Aeroplanes: list[Aeroplane], filter_words: list[str]) -> list[Aeroplane]:
    """Функция для фильтрации самолетов по стране регистрации (без учета регистра)."""
    try:
        normalized_filters = {word.strip().casefold() for word in filter_words if word.strip()}
        if not normalized_filters:
            return list(Aeroplanes)
        return [
            aeroplane
            for aeroplane in Aeroplanes
            if aeroplane.origin_country.casefold() in normalized_filters
        ]
    except Exception as e:
        print(f"Ошибка при фильтрации самолетов: {e}")
        return []

    
def get_aeroplanes_by_altitude(Aeroplanes: list[Aeroplane], altitude_range: tuple[float, float]) -> list[Aeroplane]:
    """Функция для фильтрации самолетов по высоте полета"""
    try:
        ranged_list_aeroplanes = []
        for aeroplane in Aeroplanes:
            if aeroplane.baro_altitude >= altitude_range[0] and aeroplane.baro_altitude <= altitude_range[1]:
                ranged_list_aeroplanes.append(aeroplane)
        return ranged_list_aeroplanes
    except Exception as e:
        print(f"Ошибка при фильтрации самолетов по высоте полета: {e}")
        return []


def sort_aeroplanes(ranged_aeroplanes: list[Aeroplane]) -> list[Aeroplane]:
    """Функция для сортировки самолетов по высоте полета"""
    try:
        sorted_list_aeroplanes = sorted(ranged_aeroplanes, key=lambda x: x.baro_altitude)
        return sorted_list_aeroplanes
    except Exception as e:
        print(f"Ошибка при сортировке самолетов: {e}")
        return []


def get_top_aeroplanes(sorted_aeroplanes: list[Aeroplane], top_n: int) -> list[Aeroplane]:
    """Функция для получения топ N самолетов"""
    try:
        top_list_aeroplanes = sorted_aeroplanes[:top_n]
        return top_list_aeroplanes
    except Exception as e:
        print(f"Ошибка при получении топ N самолетов: {e}")
        return []


def print_aeroplanes(aeroplanes: list[Aeroplane]) -> None:
    """Функция для вывода информации о самолетах"""
    try:
        for aeroplane in aeroplanes:
            print(aeroplane)
    except Exception as e:
        print(f"Ошибка при выводе информации о самолетах: {e}")





