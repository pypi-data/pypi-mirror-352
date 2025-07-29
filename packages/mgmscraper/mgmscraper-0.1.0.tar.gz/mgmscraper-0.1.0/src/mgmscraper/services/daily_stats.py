# daily_stats.py

from datetime import datetime
from typing import Any, Dict, List, Optional


class DailyStatsService:
    """MGM günlük meteorolojik istatistikleri sağlayan servis sınıfı."""

    def __init__(self, session, date: str):
        try:
            self.date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Geçersiz tarih formatı. 'YYYY-MM-DD' şeklinde bir tarih girilmelidir."
            )
        self.session = session
        self.formatted_date = self.date.strftime("%Y-%m-%d")

    async def _fetch_data(
        self, api_endpoint: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Veriyi tek bir noktadan çekmek için yardımcı fonksiyon.

        Args:
            api_endpoint: Veri çekilecek API endpoint'i
        """
        query_params = {"tarih": self.formatted_date}
        return await self.session.get_json(api_endpoint, query_params)

    async def get_highest_temperature(self) -> Optional[List[Dict[str, Any]]]:
        """Günün en yüksek sıcaklık değerlerini getirir."""
        return await self._fetch_data("sondurumlar/enyuksek")

    async def get_lowest_temperature(self) -> Optional[List[Dict[str, Any]]]:
        """Günün en düşük sıcaklık değerlerini getirir."""
        return await self._fetch_data("sondurumlar/endusuk")

    async def get_lowest_soil_temperature(
        self,
    ) -> Optional[List[Dict[str, Any]]]:
        """Günün en düşük toprak üstü sıcaklık değerlerini getirir."""
        return await self._fetch_data("sondurumlar/toprakustu")

    async def get_total_precipitation(self) -> Optional[List[Dict[str, Any]]]:
        """Günün toplam yağış miktarlarını getirir."""
        return await self._fetch_data("sondurumlar/toplamyagis")

    async def get_historical_extremes(
        self, merkezid: int
    ) -> Optional[Dict[str, Any]]:
        """Belirtilen merkez için seçili güne ait 1991-2020 yılları arası ekstrem değerleri getirir.

        Bu fonksiyon, seçili gün için (ay ve gün) o merkezde 1991-2020 yılları arasında ölçülmüş
        en düşük ve en yüksek sıcaklık ve yağış değerlerini döndürür.

        Args:
            merkezid: Ekstrem değerlerin alınacağı merkezin ID'si

        Note:
            Bu fonksiyon, sınıfın date özelliğindeki yıl değerini kullanmaz.
            Sadece ay ve gün bilgisi kullanılarak, 1991-2020 yılları arasındaki
            ekstrem değerler getirilir.
        """
        query_params = {
            "merkezid": merkezid,
            "ay": self.date.month,
            "gun": self.date.day,
        }
        api_endpoint = "ucdegerler"
        extreme_data = await self.session.get_json(api_endpoint, query_params)
        return (
            extreme_data[0]
            if extreme_data and isinstance(extreme_data, list)
            else None
        )
