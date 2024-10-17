import psycopg2
import sys

from psycopg2 import sql
from logger import setup_logger


logger = setup_logger(__name__)


def create_connection():
    """Создание подключения к базе данных."""
    conn = psycopg2.connect(
        dbname="samokat_data",
        user="mirea",
        password="admin",
        host="localhost",
        port="5432",
    )
    return conn


def check_database_and_tables():
    """Проверка работоспособности подключения к БД и наличия таблиц."""
    logger.info("Проверка доступа к СУБД")
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]

        logger.info(f"Подключено к базе данных: {db_name}")

        # Проверка наличия таблиц
        tables = ["categories", "products"]
        for table in tables:
            cursor.execute(
                sql.SQL(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);"
                ),
                [table],
            )
            exists = cursor.fetchone()[0]
            if exists:
                logger.info(f"Таблица '{table}' существует.")
            else:
                logger.error(f"Таблица '{table}' не найдена.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        sys.exit(1)


def fetch_categories():

    conn = create_connection()
    cursor = conn.cursor()

    fetch_query = "SELECT id, name, url FROM categories"
    cursor.execute(fetch_query)
    categories = cursor.fetchall()

    cursor.close()
    conn.close()
    return categories


def insert_product(name, price, weight, url, category_id, img_url):
    conn = create_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO products (name, price, weight, url, category_id, img_url)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO NOTHING;
    """
    try:
        cursor.execute(insert_query, (name, price, weight, url, category_id, img_url))
        conn.commit()
        logger.info(f"Добавлен товар ({name})[C_ID: {category_id}]")
    except Exception as e:
        print(f"Ошибка при добавлении товара: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_category(category):
    """Вставка категории в таблицу."""
    conn = create_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO categories (name, url, img_url)
    VALUES (%s, %s, %s)
    ON CONFLICT (name) DO NOTHING;
    """

    cursor.execute(insert_query, (category.name, category.url, category.img_url))

    conn.commit()
    cursor.close()
    conn.close()
