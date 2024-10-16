from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from prettytable import PrettyTable

from bs4 import BeautifulSoup
import time

from database import (
    create_categories_table,
    insert_category,
    fetch_categories,
    create_product_table,
    insert_product,
)


URL = "https://samokat.ru/"


class Category:
    def __init__(self, name, url, img_url):
        self.name = name
        self.url = url
        self.img_url = img_url


class Product:
    def __init__(
        self,
        category_id,
        name,
        weight,
        price,
        url,
        img_url,
        description="",
        old_price=None,
    ):
        self.category_id = category_id
        self.weight = weight
        self.name = name
        self.price = price
        self.description = description
        self.disc_price = old_price
        self.url = url
        self.img_url = img_url

    def print(self):
        print(f"{self.name} - {self.price}")
        print(f"{self.description}")
        print(f"{self.url}")
        print(f"{self.img_url}")
        print(f"Цена со скидкой: {self.old_price}")


def start_webdriver():
    chrome_options = Options()

    # Запуск браузера в headless режиме
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--start-fullscreen")
    chrome_options.add_argument("--no-proxy-server")  # Убрать прокси, если не нужно
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )

    service = Service(executable_path="./chromedriver.exe")

    #
    driver = webdriver.Chrome(service=service, options=chrome_options)
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

            print(
                f"Название: {category.name}, Ссылка: {URL + category.url}, URL изображения: {category.img_url}"
            )

    return categories


# Парсинг страницы с товарами
def parse_products(driver, url):
    # driver.get(url)
    # time.sleep(8)  # Подождем немного для полной загрузки страницы

    # main_page = driver.page_source

    # soup = BeautifulSoup(main_page, "html.parser")

    # TODO
    pass


def parse_category_products(driver: webdriver.Chrome, max_len=10):
    print("Запуск парсинга категорий")
    categories_raw = fetch_categories()[:10]

    print(f"Доступно категорий: {len(categories_raw)}")

    for category in categories_raw:
        id, name, url = category
        print(f"Парсинг категории: {name} / {url}")

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

                    insert_product(
                        name=p_name,
                        weight=product_specification,
                        price=price.split(" ")[0],
                        url=URL + a_tag["href"][1:],
                        img_url=img_url,
                        category_id=id,
                    )
                    print(f"Запись продукта {p_name} в категорию {name}")

            except Exception as e:
                print(f"Ошибка: {e}")


# Остановка приложения
def stop_app(driver):
    driver.quit()


# Основная функция запуска парсера
if __name__ == "__main__":

    driver = start_webdriver()

    parse_category_products(driver)

    # create_product_table()
    # categories = parse_categories(driver, URL)

    # table = PrettyTable()
    # table.add_column("Название", [i.name for i in categories])
    # table.add_column("Ссылка", [i.url for i in categories])

    # print(table)

    # create_categories_table()

    # for category in categories:
    #     print(f"Запись категории {category.name}")
    #     insert_category(category)

    # stop_app(driver)
