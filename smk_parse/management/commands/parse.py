from django.core.management.base import BaseCommand
from smk_parse.models import Category, Product  # Импортируйте ваши модели
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Парсер данных с сайта Samokat"

    def start_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(
            options=chrome_options
        )  # Убедитесь, что у вас установлен драйвер Chrome
        return driver

    def parse_categories(self, driver, url):
        categories = []
        driver.get(url)
        time.sleep(3)

        main_page = driver.page_source
        soup = BeautifulSoup(main_page, "html.parser")
        divs = soup.find_all("div", {"class": "CategoriesGrid_root__uIx8J"})

        for div in divs:
            a_tags = div.find_all("a", {"class": "CategoryLink_root__FXcVU"})
            for a_tag in a_tags:
                link = a_tag["href"]
                img_tag = a_tag.find("img", {"class": "Card_img__aQYei"})
                img_url = img_tag["src"] if img_tag else None
                name_tag = a_tag.find("span", {"class": "Text_text__7SbT7"})
                name = name_tag.text if name_tag else "Без названия"

                # Сохранение категории в базу данных
                category, created = Category.objects.get_or_create(
                    name=name,
                    url=f"{url}{link[1:]}",  # Здесь добавьте правильный базовый URL
                    img_url=img_url,
                )
                categories.append(category)

        return categories

    def parse_category_products(self, driver):
        categories = Category.objects.all()
        for category in categories:
            logger.info(f"Начало парсинга категории {category.name}")
            driver.get(category.url)
            time.sleep(3)

            main_page = driver.page_source
            soup = BeautifulSoup(main_page, "html.parser")
            divs = soup.find_all("div", {"class": "ProductsList_productList__jjQpU"})
            for div in divs:
                try:
                    a_tags = div.find_all("a")
                    for a_tag in a_tags:
                        img_tag = a_tag.find("img")
                        img_url = img_tag["src"] if img_tag else None
                        info_div = a_tag.find(
                            "div", {"class": "ProductCard_content__EjT48"}
                        )
                        p_name = (
                            info_div.find("div", {"class": "ProductCard_name__2VDcL"})
                            .find("span")
                            .text
                        )
                        product_specification = (
                            a_tag.find(
                                "div", {"class": "ProductCard_specification__Y0xA6"}
                            )
                            .find("span")
                            .text
                        )

                        price_div = a_tag.find(
                            "div", {"class": "ProductCardActions_text__3Uohy"}
                        ).find("span")
                        price = (
                            price_div.find("span")
                            .text.strip()
                            .replace("₽", "")
                            .replace(" ", "")
                        )
                        price = int(price)

                        # Сохранение продукта в базу данных
                        Product.objects.get_or_create(
                            name=p_name,
                            weight=product_specification,
                            price=price,
                            url=category.url + a_tag["href"][1:],
                            img_url=img_url,
                            category=category,
                        )
                except Exception as e:
                    logger.error(f"Ошибка при парсинге: {e}")
            logger.info(f"Парсинг категории {category.name} завершен.")

    def handle(self, *args, **kwargs):
        driver = self.start_webdriver()
        try:
            self.parse_categories(driver, "https://samokat.ru/")
            self.parse_category_products(driver)
        finally:
            driver.quit()
