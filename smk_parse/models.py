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

    def __str__(self):
        return self.name

    verbose_name = "Product"
    verbose_name_plural = "Products"
