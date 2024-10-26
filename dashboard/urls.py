from django.contrib import admin
from django.urls import path
from .views import ProductView, OrderView, OrderProductView

urlpatterns = [
    path("products/", view=ProductView.as_view(), name="products"),
    path("orders/<int:id>/", view=OrderView.as_view(), name="orders"),
    path(
        "bulkproduct/<int:user_id>/",
        view=OrderProductView.as_view(),
        name="bulkproduct",
    ),
]
