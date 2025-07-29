# monthly_stats.py

import locale
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

# Türkçe locale ayarı
try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "")


def get_turkish_month_names() -> List[str]:
    """Türkçe ay isimlerini döndürür."""
    return [
        datetime.strptime(str(i), "%m").strftime("%B").capitalize()
        for i in range(1, 13)
    ]


def convert_turkish_chars(text: str) -> str:
    """Türkçe karakterleri İngilizce karakterlere dönüştürür.

    Args:
        text: Dönüştürülecek metin

    Returns:
        str: Dönüştürülmüş metin

    Raises:
        TypeError: text parametresi string değilse
    """
    if not isinstance(text, str):
        raise TypeError("Metin string olmalıdır")

    turkish_chars = "çğıöşüÇĞİÖŞÜ"
    english_chars = "cgiosuCGIOSU"
    return text.translate(str.maketrans(turkish_chars, english_chars))


def normalize_city_name(city_name: str) -> str:
    """Şehir adını normalize eder.

    - Boşlukları temizler
    - İlk harfi büyük yapar
    - Türkçe karakterleri dönüştürür
    - 'Mersin' için 'İçel' dönüşümü yapar

    Args:
        city_name: Normalize edilecek şehir adı

    Returns:
        str: Normalize edilmiş şehir adı

    Raises:
        TypeError: city_name parametresi string değilse
    """
    if not isinstance(city_name, str):
        raise TypeError("Şehir adı string olmalıdır")

    city_name = convert_turkish_chars(city_name.strip().capitalize())
    return "İçel" if city_name == "Mersin" else city_name


def parse_float(value: str) -> Optional[float]:
    """String değeri float'a dönüştürür.

    Args:
        value: Dönüştürülecek string değer

    Returns:
        Optional[float]: Dönüştürülmüş float değer veya None
    """
    if not value or not value.strip():
        return None

    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


class MonthlyStatsService:
    """MGM aylık meteorolojik istatistikleri sağlayan servis sınıfı."""

    api_endpoint = "veridegerlendirme/il-ve-ilceler-istatistik.aspx?"
    turkish_month_names = get_turkish_month_names()

    def __init__(self, session, city_name: str):
        """Servis sınıfını başlatır.

        Args:
            session: HTTP istemcisi
            city_name: Şehir adı
        """
        self.session = session
        self.city_name = normalize_city_name(city_name)

    async def get_general_stats(self) -> Optional[Dict[str, Any]]:
        """Genel aylık verileri getirir.

        Returns:
            Optional[Dict[str, Any]]: Genel aylık veriler veya None
        """
        return await self._fetch_data("A")

    async def get_seasonal_norms(self) -> Optional[Dict[str, Any]]:
        """Mevsim normalleri verilerini getirir.

        Returns:
            Optional[Dict[str, Any]]: Mevsim normalleri verileri veya None
        """
        return await self._fetch_data("H")

    async def _fetch_data(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Belirtilen veri türüne göre aylık verileri getirir.

        Args:
            data_type: Veri türü ('A' veya 'H')

        Returns:
            Optional[Dict[str, Any]]: Aylık veriler veya None

        Raises:
            ValueError: Geçersiz veri türü
        """
        if data_type not in ["A", "H"]:
            raise ValueError("Geçersiz veri türü. 'A' veya 'H' olmalıdır.")

        query_params = {"k": data_type, "m": self.city_name.upper()}
        html_content = await self.session.get_html(
            self.api_endpoint, query_params
        )
        return self._parse_table(html_content)

    def _parse_table(
        self, html_content: BeautifulSoup
    ) -> Optional[Dict[str, Any]]:
        """HTML yanıtını ayrıştırarak tablo verisini uygun formata getirir.

        Args:
            html_content: HTML içeriği

        Returns:
            Optional[Dict[str, Any]]: Ayrıştırılmış tablo verisi veya None
        """
        if html_content is None:
            return None

        try:
            rows, headers = self._extract_table_data(html_content)
            if not rows or not headers:
                return None

            self._validate_headers(headers)
            return self._convert_to_dict(rows, headers)
        except Exception as e:
            print(f"Tablo ayrıştırma hatası: {e}")
            return None

    def _extract_table_data(
        self, html_content: BeautifulSoup
    ) -> Tuple[List, List]:
        """Tablonun başlıklarını ve satırlarını çıkarır.

        Args:
            html_content: HTML içeriği

        Returns:
            Tuple[List, List]: (Satırlar, Başlıklar) tuple'ı

        Raises:
            ValueError: Gerekli HTML bileşenleri bulunamadığında
        """
        try:
            tbody = html_content.find("tbody")
            thead = html_content.find("thead")
            if not tbody or not thead:
                raise ValueError("Gerekli HTML bileşenleri bulunamadı.")

            rows = tbody.find_all("tr")
            headers = [th.text.strip() for th in thead.find_all("th")]
            return rows, headers
        except Exception as e:
            print(f"HTML veri çıkarma hatası: {e}")
            return [], []

    def _validate_headers(self, headers: List[str]) -> None:
        """Tablo başlıklarını doğrular ve uyumsuzluk durumunda hata verir.

        Args:
            headers: Tablo başlıkları

        Raises:
            ValueError: Başlıklar geçersiz olduğunda
        """
        if len(headers) != 14 or headers[-1] != "Yıllık":
            raise ValueError("Tablonun sütun yapısı uyumsuz.")

        if headers[0] != self.city_name.upper():
            raise ValueError(
                f"Tablodaki il bilgisi '{headers[0]}' beklenen '{self.city_name.upper()}' ile uyuşmuyor."
            )

        del headers[0]  # Şehir bilgisini kaldır
        del headers[-1]  # 'Yıllık' sütununu kaldır

        if headers != self.turkish_month_names:
            raise ValueError("Tablodaki sütun başlıkları aylara uymuyor.")

    def _convert_to_dict(
        self, rows: List, headers: List[str]
    ) -> Dict[str, Any]:
        """Tablo verisini işleyip sözlüğe dönüştürür.

        Args:
            rows: Tablo satırları
            headers: Tablo başlıkları

        Returns:
            Dict[str, Any]: Dönüştürülmüş tablo verisi
        """
        table_data = {}
        for row in rows:
            key, values = self._parse_row(row, headers)
            if key:
                table_data[key] = values
        return table_data

    def _parse_row(
        self, row: BeautifulSoup, headers: List[str]
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Tablodaki bir satırı işler ve anahtar-değer çiftleri olarak döndürür.

        Args:
            row: Tablo satırı
            headers: Tablo başlıkları

        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]]]: (Anahtar, Değerler) tuple'ı
        """
        keys = row.find_all("th")
        cells = row.find_all("td")

        if not keys:
            return None, None

        key = self._clean_key(keys[0])

        if len(cells) == len(headers) + 1:
            del cells[-1]  # 'Yıllık' hücresini kaldır
            values = self._parse_cell_values(cells)
            return key, dict(zip(headers, values))

        return "Ölçüm Periyodu", (
            key.split("(")[-1].rstrip(")").replace(" ", "")
            if len(cells) == 1
            else None
        )

    def _clean_key(self, key_element: BeautifulSoup) -> str:
        """Satır anahtarını temizler ve gereksiz boşlukları kaldırır.

        Args:
            key_element: Anahtar elementi

        Returns:
            str: Temizlenmiş anahtar
        """
        return (
            key_element.text.strip()
            .replace("\n", "")
            .replace("\r", "")
            .replace("                 ", "")
        )

    def _parse_cell_values(
        self, cells: List[BeautifulSoup]
    ) -> Tuple[Optional[float], ...]:
        """Hücrelerdeki sayısal değerleri çıkarır, boş hücrelere 'None' atar.

        Args:
            cells: Tablo hücreleri

        Returns:
            Tuple[Optional[float], ...]: Sayısal değerler tuple'ı
        """
        try:
            values = tuple(parse_float(x.text.strip()) for x in cells)
            return values
        except Exception:
            return tuple(
                None for _ in cells
            )  # Hatalı değerler için None döner
