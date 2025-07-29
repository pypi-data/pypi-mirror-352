# stations.py

from typing import Any, Dict, List, Optional


class StationService:
    """MGM istasyon bilgilerini sağlayan servis sınıfı."""

    def __init__(self, session):
        self.session = session

    async def get_station(
        self, province_name: str, district_name: str
    ) -> Optional[Dict[str, Any]]:
        """Belirli bir il ve ilçedeki istasyon bilgilerini getirir."""
        api_endpoint = "merkezler"
        query_params = {"il": province_name, "ilce": district_name}
        station_data = await self.session.get_json(api_endpoint, query_params)
        return (
            station_data[0]
            if station_data and isinstance(station_data, list)
            else None
        )

    async def get_province_centers(self) -> Optional[List[Dict[str, Any]]]:
        """Tüm il merkezlerinin listesini getirir."""
        api_endpoint = "merkezler/iller"
        return await self.session.get_json(api_endpoint)

    async def get_province_stations(
        self, province_name: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Belirli bir ildeki tüm istasyonların listesini getirir."""
        api_endpoint = "istasyonlar/ilAdDetay"
        query_params = {"il": province_name.title()}
        return await self.session.get_json(api_endpoint, query_params)

    async def get_ski_stations(self) -> Optional[List[Dict[str, Any]]]:
        """Kayak merkezi istasyonlarının listesini getirir."""
        api_endpoint = "istasyonlar/kayakMerkezleri"
        return await self.session.get_json(api_endpoint)
