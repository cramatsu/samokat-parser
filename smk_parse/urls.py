from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.get_products, name="get_products"),
    path("products/<int:pk>/", views.get_product, name="get_product"),
    path("products/add/", views.add_product, name="add_product"),
]
