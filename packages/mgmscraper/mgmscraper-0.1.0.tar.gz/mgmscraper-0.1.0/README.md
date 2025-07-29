# MGMScraper

[![PyPI version](https://img.shields.io/pypi/v/mgmscraper.svg)](https://pypi.org/project/mgmscraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/mhmmdlsubasi/mgmscraper/publish-to-pypi.yml?branch=main)](https://github.com/mhmmdlsubasi/mgmscraper/actions)

MGMScraper is an asynchronous Python library for extracting weather and climate data from the Turkish Meteorology General Directorate (MGM) website (mgm.gov.tr). It provides a clean, modular API for retrieving observations, forecasts, statistics, and radar imagery with minimal dependencies.

---

## 🚀 Features

- **Asynchronous Data Retrieval**: Leverage modern `asyncio` patterns for high-performance scraping
- **Comprehensive Endpoints**:
  - Station information
  - Real-time observations
  - Forecast data (hourly and daily)
  - Daily and monthly statistics
  - Radar images
- **Modular Design**: Each service (e.g., `StationService`, `ForecastService`) lives in its own module, simplifying extension and maintenance
- **Built-in Rate Limiting**: Configurable request rate limiting to respect server resources
- **Robust Error Handling**: Automatic retries with exponential backoff
- **Lightweight Footprint**: Only two external dependencies: `aiohttp` and `beautifulsoup4`

---

## ⚙️ Installation

```bash
pip install mgmscraper
```

---

## 🔧 Quick Start

### Basic Usage

```python
import asyncio
from mgmscraper import HttpClient, StationService

async def main():
    async with HttpClient() as session:
        station_service = StationService(session)

        # Get all province centers
        provinces = await station_service.get_province_centers()
        print(f"Found {len(provinces)} provinces")

        # Get stations in a specific province
        istanbul_stations = await station_service.get_province_stations("İstanbul")
        print(f"Found {len(istanbul_stations)} stations in İstanbul")

if __name__ == "__main__":
    asyncio.run(main())
```

### Weather Observations

```python
import asyncio
from mgmscraper import HttpClient, ObservationService

async def main():
    async with HttpClient() as session:
        obs_service = ObservationService(session)

        # Get current weather for İstanbul (province plate code: 34)
        istanbul_weather = await obs_service.get_by_province_plate(34)

        for station in istanbul_weather:
            print(f"{station['istNo']}: {station['sicaklik']}°C")

if __name__ == "__main__":
    asyncio.run(main())
```

### Weather Forecasts

```python
import asyncio
from mgmscraper import HttpClient, ForecastService

async def main():
    async with HttpClient() as session:
        forecast_service = ForecastService(session)

        # Get hourly forecast for a station (example station ID: 17130)
        hourly_forecast = await forecast_service.get_hourly_forecast(17130)
        if hourly_forecast:
            print(f"Hourly forecast for {hourly_forecast['merkez']}:")
            for hour in hourly_forecast["tahmin"]:
                print(f"  {hour['tarih']}: {hour['sicaklik']}°C")

if __name__ == "__main__":
    asyncio.run(main())
```

### Daily Statistics

```python
import asyncio
from mgmscraper import HttpClient, DailyStatsService

async def main():
    async with HttpClient() as session:
        # Get statistics for January 1, 2024
        daily_stats = DailyStatsService(session, "2024-01-01")

        # Get highest temperatures of the day
        highest_temps = await daily_stats.get_highest_temperature()
        if highest_temps:
            print("Highest temperatures:")
            for record in highest_temps[:5]:  # Show top 5
                print(f"  {record['istAd']}: {record['deger']}°C")

if __name__ == "__main__":
    asyncio.run(main())
```

### Monthly Statistics

```python
import asyncio
from mgmscraper import HttpClient, MonthlyStatsService

async def main():
    async with HttpClient() as session:
        monthly_stats = MonthlyStatsService(session, "İstanbul")

        # Get general monthly statistics
        general_stats = await monthly_stats.get_general_stats()
        if general_stats:
            print("İstanbul Monthly Statistics:")
            for param, values in general_stats.items():
                print(f"  {param}: {values}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Radar Images

```python
import asyncio
from mgmscraper import HttpClient, RadarService

async def main():
    async with HttpClient() as session:
        radar_service = RadarService(session)

        # Get available radar details
        radar_details = await radar_service.get_details()
        print("Available radars:")
        for radar_name in radar_details.keys():
            print(f"  - {radar_name}")

        # Get radar image (example: İstanbul radar, PPI product, image #1)
        image_data = await radar_service.get_image("İstanbul", "ppi", 1)
        if image_data:
            with open("istanbul_radar.jpg", "wb") as f:
                f.write(image_data)
            print("Radar image saved as istanbul_radar.jpg")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📋 Available Services

### StationService

- `get_station(province_name, district_name)`: Get specific station info
- `get_province_centers()`: Get all province centers
- `get_province_stations(province_name)`: Get all stations in a province
- `get_ski_stations()`: Get ski resort stations

### ObservationService

- `get_by_istno(sondurumIstNo)`: Get current weather by station ID
- `get_by_merkezid(merkezid)`: Get current weather by center ID
- `get_by_province_plate(plate_code)`: Get all current weather data for a province
- `get_province_centers()`: Get province center list
- `get_province_stations(province_name)`: Get station list for a province
- `get_snow_depth()`: Get snow depth observations

### ForecastService

- `get_hourly_forecast(saatlikTahminIstNo)`: Get hourly forecast for a station
- `get_daily_forecast(gunlukTahminIstNo)`: Get daily forecast for a station

### DailyStatsService

- `get_highest_temperature()`: Get daily highest temperatures
- `get_lowest_temperature()`: Get daily lowest temperatures
- `get_lowest_soil_temperature()`: Get daily lowest soil temperatures
- `get_total_precipitation()`: Get daily total precipitation
- `get_historical_extremes(merkezid)`: Get historical extremes for a date

### MonthlyStatsService

- `get_general_stats()`: Get general monthly statistics
- `get_seasonal_norms()`: Get seasonal norm data

### RadarService

- `get_details()`: Get available radar information
- `get_image(radar_name, product, number)`: Get radar images

---

## ⚡ Advanced Configuration

### Custom HTTP Client Settings

```python
from mgmscraper import HttpClient

# Configure client with custom settings
async with HttpClient(
    timeout=120,              # Request timeout in seconds
    max_retries=5,           # Maximum retry attempts
    calls_per_second=1.0,    # Rate limiting
    max_connections=50,      # Connection pool size
    ssl_verify=True          # SSL verification
) as session:
    # Your code here
    pass
```

### Error Handling

```python
import asyncio
from mgmscraper import HttpClient, ObservationService

async def main():
    try:
        async with HttpClient() as session:
            obs_service = ObservationService(session)
            data = await obs_service.get_by_province_plate(34)

            if data is None:
                print("No data available")
            else:
                print(f"Retrieved {len(data)} observations")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m "Add amazing feature"`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code follows the existing style and includes appropriate documentation.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This library is for educational and research purposes. Please respect MGM's servers by:

- Using appropriate rate limiting (default: 2 requests/second)
- Not making excessive requests
- Following MGM's terms of service

---

## 🔗 Links

- **GitHub**: [github.com/mhmmdlsubasi/mgmscraper](https://github.com/mhmmdlsubasi/mgmscraper)
- **PyPI**: [pypi.org/project/mgmscraper](https://pypi.org/project/mgmscraper)
- **Issues**: [github.com/mhmmdlsubasi/mgmscraper/issues](https://github.com/mhmmdlsubasi/mgmscraper/issues)
- **Documentation**: [mgmscraper.readthedocs.io](https://mgmscraper.readthedocs.io)

---

## 📊 Data Sources

All data is sourced from the Turkish Meteorology General Directorate (MGM):

- Website: [mgm.gov.tr](https://mgm.gov.tr)
- API Base: [servis.mgm.gov.tr](https://servis.mgm.gov.tr)

---
