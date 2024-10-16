import psycopg2
from psycopg2 import sql


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


def fetch_categories():

    conn = create_connection()
    cursor = conn.cursor()

    fetch_query = "SELECT id, name, url FROM categories"
    cursor.execute(fetch_query)
    categories = cursor.fetchall()

    cursor.close()
    conn.close()
    return categories


def create_product_table():
    conn = create_connection()
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        price NUMERIC(10, 2) NOT NULL,
        weight TEXT,
        url TEXT UNIQUE NOT NULL,
        category_id INT NOT NULL,
        img_url TEXT,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()


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
        print(f"Товар {name} успешно добавлен.")
    except Exception as e:
        print(f"Ошибка при добавлении товара: {e}")
    finally:
        cursor.close()
        conn.close()


def create_categories_table():

    conn = create_connection()
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        url TEXT NOT NULL,
        img_url TEXT
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
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
