import os
import time
import logging

from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from smk_parse.models import Product, Category
from logger import setup_logger  # Импорт логгера

URL = "https://samokat.ru/"
logger = setup_logger()  # Настройка логгера


def start_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )

    driver = webdriver.Remote(
        command_executor="http://localhost:4444/wd/hub", options=chrome_options
    )
    return driver


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

            # Сохраняем продукт в базу данных
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

    def handle(self, *args, **kwargs):
        logger.info("Начинаю парсинг продуктов по категориям...")

        driver = start_webdriver()

        try:
            categories = (
                Category.objects.all()
            )  # Получение всех категорий из базы данных

            for category in categories:
                parse_category_products(
                    driver, category
                )  # Парсинг продуктов по категории
                logger.info(
                    f"Парсинг продуктов для категории {category.name} завершен."
                )

        except Exception as e:
            logger.error(f"Ошибка при парсинге продуктов: {e}")
        finally:
            driver.quit()
