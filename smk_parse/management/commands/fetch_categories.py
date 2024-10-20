import os
import time

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from smk_parse.models import Category
from logger import setup_logger

from .utils.webdriver import start_webdriver

URL = "https://samokat.ru/"
logger = setup_logger()


def parse_categories(driver, url):
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

            category, created = Category.objects.get_or_create(
                name=name, defaults={"url": f"{URL}{link[1:]}", "img_url": img_url}
            )
            if created:
                logger.info(f"Категория '{name}' успешно добавлена.")
            else:
                logger.info(f"Категория '{name}' уже существует.")


class Command(BaseCommand):
    help = "Получает и сохраняет категории с сайта"

    def handle(self, *args, **kwargs):
        logger.info("Начинаю получение категорий...")
        driver = start_webdriver()

        try:
            parse_categories(driver, URL)
            logger.info("Категории успешно получены и сохранены.")
        finally:
            driver.quit()
