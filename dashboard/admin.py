from django.contrib import admin
from .models import Product, Order


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item_name", "quantity", "unit_price")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product")


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
