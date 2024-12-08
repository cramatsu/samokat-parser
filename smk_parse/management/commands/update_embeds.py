from django.core.management.base import BaseCommand
from smk_parse.models import Product
from sentence_transformers import SentenceTransformer


class Command(BaseCommand):
    help = "Обновление эмбеддингов товаров"

    def handle(self, *args, **kwargs):
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        products = Product.objects.all()

        for product in products:
            product.save_embedding(model)
            self.stdout.write(f"Обновлён эмбеддинг для: {product.name}")
