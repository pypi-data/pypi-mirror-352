"""
MGM Scraper - Türkiye Meteoroloji Genel Müdürlüğü veri çekme kütüphanesi

Bu paket, Meteoroloji Genel Müdürlüğü'nün (MGM) API'lerinden ve web sitelerinden
veri çekmek için kullanılır. Aşağıdaki modüller aracılığıyla çeşitli hava durumu
ve istasyon verileri alınabilir.
"""

from .core.http_client import HttpClient
from .services.daily_stats import DailyStatsService
from .services.forecasts import ForecastService
from .services.monthly_stats import MonthlyStatsService
from .services.observations import ObservationService
from .services.radar import RadarService
from .services.stations import StationService

__version__ = "0.1.0"

# Kullanıcıların bu sınıflara kolay erişimi için
__all__ = [
    "HttpClient",
    "RadarService",
    "DailyStatsService",
    "MonthlyStatsService",
    "StationService",
    "ForecastService",
    "ObservationService",
]
