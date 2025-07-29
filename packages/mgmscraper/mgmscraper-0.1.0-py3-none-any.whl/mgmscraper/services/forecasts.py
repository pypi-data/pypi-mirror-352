# forecasts.py

from typing import Any, Dict, Optional


class ForecastService:
    """MGM hava durumu tahminlerini sağlayan servis sınıfı."""

    def __init__(self, session):
        self.session = session

    async def get_hourly_forecast(
        self, saatlikTahminIstNo: int
    ) -> Optional[Dict[str, Any]]:
        """Belirli bir istasyon için saatlik hava durumu tahminini getirir.

        Args:
            saatlikTahminIstNo: Saatlik tahmin verisi alınacak istasyonun ID'si
        """
        api_endpoint = "tahminler/saatlik"
        query_params = {"istno": saatlikTahminIstNo}
        forecast_data = await self.session.get_json(api_endpoint, query_params)
        return (
            forecast_data[0]
            if forecast_data and isinstance(forecast_data, list)
            else None
        )

    async def get_daily_forecast(
        self, gunlukTahminIstNo: int
    ) -> Optional[Dict[str, Any]]:
        """Belirli bir istasyon için günlük hava durumu tahminini getirir.

        Args:
            gunlukTahminIstNo: Günlük tahmin verisi alınacak istasyonun ID'si
        """
        api_endpoint = "tahminler/gunluk"
        query_params = {"istno": gunlukTahminIstNo}
        forecast_data = await self.session.get_json(api_endpoint, query_params)
        return (
            forecast_data[0]
            if forecast_data and isinstance(forecast_data, list)
            else None
        )
