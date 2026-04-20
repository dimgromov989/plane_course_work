import requests
from base_plane import AbstractPlaneBase
import json


class AeroplanesAPI(AbstractPlaneBase):
    def __init__(self) -> None:
        """Инициализация атрибутов класса"""
        super().__init__()
        self._aeroplanes = None

    
    def _connection_api(self, url: str, params: dict) -> dict:
        """метод соединения с API"""
        headers = {'User-Agent': 'plane_course_work/1.0'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Ошибка при соединении с API: {response.status_code}")
        return response.json()

    def get_aeroplanes(self, country: str) -> dict:
        """метод получения информации о самолетах отдельно"""
        coordinate = self._connection_api(self._openstreetmap_url, {'country': country, 'format': 'json', 'limit': '10'})
        if not coordinate:
            raise ValueError(f'Не удалось найти границы для страны: {country}')

        params_opensky = {
            'lamin': coordinate[0].get('boundingbox')[0],
            'lamax': coordinate[0].get('boundingbox')[1],
            'lomin': coordinate[0].get('boundingbox')[2],
            'lomax': coordinate[0].get('boundingbox')[3]
        }
        response_opensky = self._connection_api(self._opensky_url, params_opensky)
        return response_opensky


    def save_aeroplanes(self, aeroplanes: dict) -> None:
        with open('data_plane.json', 'w', encoding='utf-8') as file:
            json.dump(aeroplanes, file, ensure_ascii=False, indent=4)





    
    














