from rest_framework import serializers
from django.utils import timezone
from .models import Product, Order


class ProductSerailizer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "user",
            "item_name",
            "quantity",
            "unit_price",
            "instruction",
            "total_price",
        )

    def get_total_price(self, obj: Product):
        return obj.quantity * obj.unit_price

    def create(self, validated_data):
        user_id = validated_data.get("user_id")
        obj = super().create(validated_data)
        Order.objects.create(product=obj, user_id=user_id)
        return obj


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerailizer()
    order_id = serializers.IntegerField(source="id")

    class Meta:
        model = Order
        fields = ("order_id", "product")


class BulkProductSerializer(serializers.Serializer):
    products = ProductSerailizer(many=True)
    user_id = serializers.IntegerField()

    def validate(self, data):
        user_id = data.get("user_id")
        today = timezone.now().date()
        duplicate_items = []
        item_names_seen = set()

        for product_data in data["products"]:
            item_name = product_data["item_name"]

            if item_name in item_names_seen:
                duplicate_items.append(item_name)
            else:
                item_names_seen.add(item_name)

            product_obj = Product.objects.filter(
                user_id=user_id, item_name=item_name, created_at__date=today
            ).last()

            if product_obj:
                duplicate_items.append(item_name)

        if duplicate_items:
            duplicates_message = ", ".join(set(duplicate_items))
            raise serializers.ValidationError(
                {
                    "message": f"Cannot order the same items twice in a day: {duplicates_message}"
                }
            )

        return data

    def create(self, validated_data):
        user_id = validated_data.get("user_id")
        products_data = validated_data.pop("products")
        created_products = []

        for product_data in products_data:
            product_data["user_id"] = user_id
            product = ProductSerailizer().create(product_data)
            created_products.append(product)

        return created_products
