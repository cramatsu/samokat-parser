from django.core.management.base import BaseCommand
from smk_parse.models import Product
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Command(BaseCommand):
    help = "Поиск товаров по запросу"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str, help="Введите текст запроса")

    def handle(self, *args, **kwargs):
        query = kwargs["query"]

        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        # Векторизация запроса
        query_embedding = model.encode(query)

        # Получение товаров и их эмбеддингов
        products = Product.objects.all()
        product_embeddings = [
            (product, np.frombuffer(product.embedding, dtype=np.float32))
            for product in products
            if product.embedding
        ]

        # Сравнение схожести
        similarities = [
            (product, cosine_similarity([query_embedding], [embedding])[0][0])
            for product, embedding in product_embeddings
        ]

        # Сортировка и вывод
        sorted_results = sorted(similarities, key=lambda x: x[1], reverse=True)
        for product, score in sorted_results[:10]:
            self.stdout.write(f"{product.name} ({score:.2f})")
