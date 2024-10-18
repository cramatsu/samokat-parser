import os
import time

from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from smk_parse.models import Category
from logger import setup_logger  # Импорт логгера

URL = "https://samokat.ru/"
logger = setup_logger()  # Настройка логгера


def is_running_in_docker():
    """Проверяет, работает ли приложение внутри контейнера Docker."""
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


def start_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )

    command_executor_url = (
        "http://selenium-chrome:4444/wd/hub"
        if is_running_in_docker()
        else "http://localhost:4444/wd/hub"
    )

    driver = webdriver.Remote(
        command_executor=command_executor_url, options=chrome_options
    )
    return driver


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

            # Сохраняем категорию в базу данных
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
