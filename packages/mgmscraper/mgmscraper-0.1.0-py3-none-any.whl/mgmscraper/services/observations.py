# observations.py

from typing import Any, Dict, List, Optional


class ObservationService:
    """MGM anlık hava durumu gözlemlerini sağlayan servis sınıfı."""

    def __init__(self, session):
        self.session = session

    async def _get_station_data(
        self, query_param: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Tek bir istasyonun anlık hava durumu gözlem verisini getirir.

        Args:
            query_param: Sorgu parametresi ('istno' veya 'merkezid' ve değeri)
        """
        api_endpoint = "sondurumlar"
        observation_data = await self.session.get_json(
            api_endpoint, query_param
        )
        return (
            observation_data[0]
            if observation_data and isinstance(observation_data, list)
            else None
        )

    async def get_by_istno(
        self, sondurumIstNo: int
    ) -> Optional[Dict[str, Any]]:
        """Belirli bir istasyon için anlık hava durumu gözlemlerini getirir.
        İstasyonun sondurumIstNo değeri kullanılarak sorgu yapılır.

        Args:
            sondurumIstNo: İstasyonun sondurumIstNo değeri
        """
        return await self._get_station_data({"istno": sondurumIstNo})

    async def get_by_merkezid(self, merkezid: int) -> Optional[Dict[str, Any]]:
        """Belirli bir istasyon için anlık hava durumu gözlemlerini getirir.
        İstasyonun merkezid değeri kullanılarak sorgu yapılır.

        Args:
            merkezid: İstasyonun merkezid değeri
        """
        return await self._get_station_data({"merkezid": merkezid})

    async def get_by_province_plate(
        self, ilPlaka: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Belirli bir il için tüm anlık hava durumu gözlemlerini getirir.

        Args:
            ilPlaka: Anlık gözlem verisi alınacak ilin plaka kodu
        """
        api_endpoint = "sondurumlar/ilTumSondurum"
        query_params = {"ilPlaka": ilPlaka}
        return await self.session.get_json(api_endpoint, query_params)

    async def get_province_centers(self) -> Optional[List[Dict[str, Any]]]:
        """Tüm il merkezlerinin listesini getirir."""
        api_endpoint = "sondurumlar/ilmerkezleri"
        return await self.session.get_json(api_endpoint)

    async def get_province_stations(
        self, province_name: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Belirli bir ildeki tüm istasyonların listesini getirir.

        Args:
            province_name: İstasyon listesi alınacak ilin adı
        """
        api_endpoint = "merkezler/ililcesi"
        query_params = {"il": province_name.title()}
        return await self.session.get_json(api_endpoint, query_params)

    async def get_snow_depth(self) -> Optional[List[Dict[str, Any]]]:
        """Kar yüksekliği gözlemlerini getirir."""
        api_endpoint = "sondurumlar/kar"
        return await self.session.get_json(api_endpoint)
