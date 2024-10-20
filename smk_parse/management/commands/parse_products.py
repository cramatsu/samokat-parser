import time
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from smk_parse.models import Product, Category
from logger import setup_logger

from .utils.webdriver import start_webdriver

URL = "https://samokat.ru/"
logger = setup_logger()


def parse_category_products(driver, category):
    logger.info(f"Парсинг продуктов для категории: {category.name}")
    driver.get(category.url)
    time.sleep(3)

    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html.parser")
    divs = soup.find_all("div", {"class": "ProductsList_productList__jjQpU"})

    for div in divs:
        a_tags = div.find_all("a")
        for a_tag in a_tags:
            img_tag = a_tag.find("img")
            img_url = img_tag["src"] if img_tag else None

            info_div = a_tag.find("div", {"class": "ProductCard_content__EjT48"})
            p_name = (
                info_div.find("div", {"class": "ProductCard_name__2VDcL"})
                .find("span")
                .text
            )

            product_specification = (
                a_tag.find("div", {"class": "ProductCard_specification__Y0xA6"})
                .find("span")
                .text
            )
            price_div = a_tag.find(
                "div", {"class": "ProductCardActions_text__3Uohy"}
            ).find("span")
            outer_span = price_div.find("span")
            price = int(outer_span.text.replace("₽", "").replace(" ", "").strip())

            Product.objects.update_or_create(
                name=p_name,
                defaults={
                    "weight": product_specification,
                    "price": price,
                    "url": URL + a_tag["href"][1:],
                    "img_url": img_url,
                    "category": category,
                },
            )
            logger.info(f"Продукт '{p_name}' успешно добавлен.")


class Command(BaseCommand):
    help = "Парсит продукты по сохранённым категориям"

    def add_arguments(self, parser):

        parser.add_argument(
            "--limit", type=int, default=None, help="Лимит категорий для парсинга"
        )

    def handle(self, *args, **kwargs):
        limit = kwargs.get("limit")
        logger.info(f"Начинаю парсинг продуктов по категориям (лимит: {limit})...")

        driver = start_webdriver()

        try:

            categories = Category.objects.all()

            if limit:
                categories = categories[:limit]

            for category in categories:
                parse_category_products(driver, category)
                logger.info(
                    f"Парсинг продуктов для категории {category.name} завершен."
                )

        except Exception as e:
            logger.error(f"Ошибка при парсинге продуктов: {e}")
        finally:
            driver.quit()
