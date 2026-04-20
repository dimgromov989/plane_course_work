from abc import ABC, abstractmethod
import requests


class AbstractPlaneBase(ABC):

    def __init__(self) -> None:
        self._openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self._opensky_url = 'https://opensky-network.org/api/states/all'
    
    @abstractmethod
    def _connection_api(self, url: str, params: dict) -> dict:
        """Метод для соединения с API"""
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str, ) -> dict:
        """метод получения информации о самолетах отдельно в абстрактном классе"""
        pass 
