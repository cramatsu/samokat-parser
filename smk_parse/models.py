from django.db import models
from django.contrib import admin


class Category(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    img_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    weight = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    img_url = models.URLField(blank=True, null=True)
    embedding = models.BinaryField(null=True)

    def __str__(self):
        return self.name

    def save_embedding(self, model):
        """Сохранение эмбеддинга в базу"""
        text = self.name
        embedding = model.encode(text).tobytes()
        self.embedding = embedding
        self.save()

    verbose_name = "Product"
    verbose_name_plural = "Products"
