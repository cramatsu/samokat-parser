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

            try:

                price_span = a_tag.find(
                    "span", {"class": "ProductCardActions_oldPrice__d7vDY"}
                )

                if price_span:

                    raw_price = (
                        price_span.text.replace("₽", "").replace("\xa0", "").strip()
                    )
                    price = int(raw_price)
                else:

                    price_container = a_tag.find(
                        "div", {"class": "ProductCardActions_text__3Uohy"}
                    )
                    if price_container:
                        regular_price_span = price_container.find("span")
                        if regular_price_span:
                            raw_price = (
                                regular_price_span.text.replace("₽", "")
                                .replace("\xa0", "")
                                .strip()
                            )
                            price = int(raw_price)
                        else:
                            price = 0
                    else:
                        price = 0
                        logger.warning("Не найден контейнер цены для продукта")

            except Exception as e:
                price = 0
                logger.error(f"Ошибка при получении цены: {e}")

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
            import traceback

            logger.error(f"Ошибка при парсинге продуктов: {e}")
            logger.error(traceback.format_exc())
        finally:
            driver.quit()
