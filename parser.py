import os
import time

import argparse as ap

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from database import (
    insert_category,
    fetch_categories,
    insert_product,
    check_database_and_tables,
)

from logger import setup_logger

logger = setup_logger()

URL = "https://samokat.ru/"


class Category:
    def __init__(self, name, url, img_url):
        self.name = name
        self.url = url
        self.img_url = img_url


def is_running_in_docker():
    """
    Проверяет, работает ли приложение внутри контейнера Docker.
    Возвращает True, если в контейнере, иначе False.
    """
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

    logger.info("Подключение к драйверу")
    driver = webdriver.Remote(command_executor_url, options=chrome_options)
    logger.info("Подключено")

    return driver


def parse_categories(driver, url):
    categories: list[Category] = []
    driver.get(url)
    time.sleep(3)

    main_page = driver.page_source
    soup = BeautifulSoup(main_page, "html.parser")

    # Получаем div'ы с категориями
    divs = soup.find_all("div", {"class": "CategoriesGrid_root__uIx8J"})

    for div in divs:
        # Находим все элементы <a> внутри div
        a_tags = div.find_all("a", {"class": "CategoryLink_root__FXcVU"})
        for a_tag in a_tags:
            # Извлекаем название, ссылку и URL изображения
            link = a_tag["href"]

            # Извлечение URL изображения
            img_tag = a_tag.find("img", {"class": "Card_img__aQYei"})
            img_url = img_tag["src"] if img_tag else None

            # Извлечение названия из <span> внутри <a>
            name_tag = a_tag.find("span", {"class": "Text_text__7SbT7"})
            name = name_tag.text if name_tag else "Без названия"

            # Создаем экземпляр Category и добавляем в список
            category = Category(name=name, url=f"{URL}{link[1:]}", img_url=img_url)
            categories.append(category)

    return categories


def parse_category_products(driver: webdriver.Chrome, max_len=10):
    logger.info("Запуск парсинга категорий")

    categories_raw = fetch_categories()[:max_len]

    logger.warning(f"Лимит категорий: {max_len}")
    logger.info(f"Доступно категорий: {len(categories_raw)}")

    for category in categories_raw:
        id, name, url = category
        logger.info(f"Начало парсинга категории {name} ({id})")

        driver.get(url)
        time.sleep(3)

        mp = driver.page_source

        soup = BeautifulSoup(mp, "html.parser")

        divs = soup.find_all("div", {"class": "ProductsList_productList__jjQpU"})

        if len(divs) > max_len:
            divs = divs[:max_len]

        for div in divs:
            try:
                a_tags = div.find_all("a")

                for a_tag in a_tags:
                    img_tag = a_tag.find("img")
                    img_url = img_tag["src"]

                    info_div = a_tag.find(
                        "div", {"class": "ProductCard_content__EjT48"}
                    )

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
                    inner_span = price_div.find("span")

                    if inner_span:
                        price = outer_span.text.strip()
                    else:
                        price = outer_span.text.strip()

                    price = int(price.replace("₽", "").replace(" ", ""))

                    insert_product(
                        name=p_name,
                        weight=product_specification,
                        price=price,
                        url=URL + a_tag["href"][1:],
                        img_url=img_url,
                        category_id=id,
                    )

            except Exception as e:
                print(f"Ошибка: {e}")
        logger.info(f"Категория {name} завершена")


if __name__ == "__main__":

    parser = ap.ArgumentParser(description="Парсер данных с сайта")

    parser.add_argument(
        "--parse-categories",
        action="store_true",
        help="Если указано, категории будут спарсены с сайта",
    )

    args = parser.parse_args()

    check_database_and_tables()

    driver = start_webdriver()

    if args.parse_categories:
        logger.info("Парсинг категорий")
        categories = parse_categories(driver, URL)

        logger.info("Запись категорий")

        for category in categories:
            logger.info(f"Категория {category.name} записана")
            insert_category(category)
        logger.info("Категории записаны")

    parse_category_products(driver)

    driver.quit()
