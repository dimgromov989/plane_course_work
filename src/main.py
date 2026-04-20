from plane_info import AeroplanesAPI
from work_with_plane import Aeroplane
from user_interaction import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    sort_aeroplanes,
    get_top_aeroplanes,
    print_aeroplanes,
)
from managment import JSONSaver


def _parse_altitude_range(raw: str) -> tuple[float, float]:
    """Парсит строку вида 100000 - 150000 в кортеж"""
    parts = [p.strip() for p in raw.replace(",", ".").split("-") if p.strip()]
    if len(parts) != 2:
        raise ValueError("Диапазон должен быть в формате: <min> - <max>")
    return float(parts[0]), float(parts[1])


def user_interaction() -> None:
    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    filter_words = [
        word.strip()
        for word in input(
            "Введите названия стран для фильтрации (через запятую, например: United States, Germany): "
        ).split(",")
        if word.strip()
    ]
    altitude_range = _parse_altitude_range(
        input("Введите диапазон высот полета (пример: 100000 - 150000): ")
    )

    api = AeroplanesAPI()
    raw_response = api.get_aeroplanes(country)
    aeroplanes = [
        plane
        for plane in Aeroplane.cast_to_object_list(raw_response)
        if plane._valid_data() and plane.baro_altitude > 0
    ]

    json_saver = JSONSaver()
    for aeroplane in aeroplanes:
        json_saver.add_aeroplane(aeroplane)

    filtered_aeroplanes = filter_aeroplanes(aeroplanes, filter_words) if filter_words else aeroplanes
    ranged_aeroplanes = get_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)
    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)
    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)

    print_aeroplanes(top_aeroplanes)


if __name__ == "__main__":
    user_interaction()
