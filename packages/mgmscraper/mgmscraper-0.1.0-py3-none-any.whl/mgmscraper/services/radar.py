# radar.py
import asyncio


class RadarService:
    def __init__(self, session):
        self.session = session
        self._radar_details_cache = None

    async def _find_short_name(self, radar_name: str, radar_details: dict):
        """
        Verilen radar adı için kısa adını bulur.

        :param radar_name: Radar adı
        :param radar_details: Radar detayları
        :return: Radar adı ve kısa adı
        :raises ValueError: Radar adı bulunamazsa
        """
        radar_name_formatted = radar_name.strip().capitalize()

        if radar_name_formatted in radar_details:
            return (
                radar_name_formatted,
                radar_details[radar_name_formatted]["shortName"],
            )

        radar_name_lower = radar_name.strip().lower()
        for radar_name_key, details in radar_details.items():
            if details["shortName"] == radar_name_lower:
                return radar_name_key, radar_name_lower

        raise ValueError(f"Radar adı '{radar_name}' bulunamadı.")

    async def _check_product_support(
        self, product: str, radar_details: dict, radar_name: str
    ):
        """
        Ürünün radar tarafından desteklenip desteklenmediğini kontrol eder.

        :param product: Ürün adı
        :param radar_details: Radar detayları
        :param radar_name: Radar adı
        :raises ValueError: Ürün desteklenmiyorsa
        """
        if product not in radar_details[radar_name]["supportedProductTypes"]:
            raise ValueError(
                f"Ürün '{product}' radar '{radar_name}' tarafından desteklenmiyor."
            )

    async def get_image(self, radar_name: str, product: str, number: int):
        """
        Verilen radar adı ve ürün için görüntü alır.

        :param radar_name: Radar adı
        :param product: Ürün adı
        :param number: Görüntü sırası (1-15 arası)
        :return: Görüntü verisi
        :raises ValueError: Hatalı ürün türü veya numara
        """
        if self._radar_details_cache is None:
            self._radar_details_cache = await self.get_details()

        radar_details = self._radar_details_cache

        radar_name_key, short_name = await self._find_short_name(
            radar_name, radar_details
        )
        await self._check_product_support(
            product, radar_details, radar_name_key
        )

        if not isinstance(number, int) or not 1 <= number <= 15:
            raise ValueError(
                "Görüntü sırası 1 ile 15 arasında bir tam sayı olmalıdır."
            )

        api_endpoint = f"FTPDATA/uzal/radar/{short_name}/{short_name}{product}{number}.jpg"
        return await self.session.get_jpeg(api_endpoint)

    async def get_details(self):
        """
        Radar detaylarını asenkron olarak getirir.
        :return: Radar detayları sözlüğü
        """
        # Cache kontrolü - eğer radar detayları zaten alınmışsa tekrar istek yapmayalım
        if self._radar_details_cache is not None:
            return self._radar_details_cache

        api_endpoint = "sondurum/radar.aspx"
        try:
            # Ana radar sayfasını getir
            response = await self.session.get_html(api_endpoint)
            radar_links = response.find(id="cph_body_pRadar").find_all("a")

            # Radar URL'lerini oluştur
            radar_urls = [
                f"{api_endpoint}{radar_link['href']}"
                for radar_link in radar_links
            ]

            # Tüm radar bağlantılarını paralel olarak getir
            radar_responses = await asyncio.gather(
                *[
                    self.session.get_html(radar_url)
                    for radar_url in radar_urls
                ],
                return_exceptions=True,  # Hata durumunda diğer isteklerin devam etmesini sağla
            )

            radar_details = {}
            for i, radar_response in enumerate(radar_responses):
                # Hata kontrolü yap
                if isinstance(radar_response, Exception):
                    print(
                        f"Hata: {radar_urls[i]} için veri alınamadı: {str(radar_response)}"
                    )
                    continue

                try:
                    # Radar adını bul
                    radar_name = (
                        radar_response.find(id="sfB")
                        .find("strong")
                        .text.strip()
                    )

                    # Kısa adı bul
                    img_elem = radar_response.find(id="cph_body_imgResim")
                    if not img_elem or "src" not in img_elem.attrs:
                        continue

                    short_name = img_elem["src"].split("/")[4]

                    # Desteklenen ürün tiplerini bul
                    try:
                        image_types_elem = radar_response.find(
                            id="cph_body_pUrun"
                        )
                        if image_types_elem:
                            image_types_elements = image_types_elem.find_all(
                                "a", href=True
                            )
                            supported_product_types = []

                            for item in image_types_elements:
                                href = item.get("href")
                                if href and "&" in href:
                                    parts = href.split("&")
                                    if len(parts) > 2:
                                        product_type = (
                                            parts[2]
                                            .split("=")[1]
                                            .split("#")[0]
                                        )
                                        if product_type == "wind":
                                            product_type = "rzg"
                                        supported_product_types.append(
                                            product_type
                                        )
                        else:
                            supported_product_types = ["ppi"]
                    except (AttributeError, IndexError):
                        supported_product_types = ["ppi"]

                    # Detayları sözlüğe ekle
                    radar_details[radar_name] = {
                        "shortName": short_name,
                        "supportedProductTypes": supported_product_types,
                    }
                except Exception as e:
                    print(
                        f"Hata: {radar_urls[i]} için işleme hatası: {str(e)}"
                    )
                    continue

            # Sonuçları önbelleğe al
            self._radar_details_cache = radar_details
            return radar_details

        except Exception as e:
            print(f"Radar detayları getirilirken hata oluştu: {str(e)}")
            # Hata durumunda boş sözlük dön veya daha önce önbelleğe alınmış veriyi kullan
            return (
                self._radar_details_cache if self._radar_details_cache else {}
            )
