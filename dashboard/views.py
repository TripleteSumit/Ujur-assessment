from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order
from .serializer import ProductSerailizer, OrderSerializer, BulkProductSerializer


class ProductView(APIView):
    serializer_class = ProductSerailizer

    def get(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"status": "failed", "message": "user_id is a required query param"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product_qs = Product.objects.filter(user_id=user_id)
        serializer = self.serializer_class(product_qs, many=True)

        return Response(
            {
                "status": "success",
                "message": "successfully retrieve the products",
                "data": serializer.data,
            }
        )

    def post(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"status": "failed", "message": "user_id is a required query param"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_obj = (
            Product.objects.filter(
                user_id=user_id,
                item_name__exact=serializer.validated_data.get("item_name"),
            )
            .values("created_at")
            .last()
        )
        if product_obj:
            last_order_day = datetime.strptime(
                (product_obj["created_at"]).strftime("%d%m%Y"), "%d%m%Y"
            )
            current_day = datetime.strptime(datetime.now().strftime("%d%m%Y"), "%d%m%Y")
            if current_day <= last_order_day:
                return Response(
                    {
                        "staus": "failed",
                        "message": "Can't order the same item twice in a day",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        serializer.save(user_id=user_id)

        return Response(
            {
                "status": "success",
                "message": "Product created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderView(APIView):
    serializer_class = OrderSerializer

    def get(self, request, id):
        order_qs = Order.objects.filter(user_id=id).select_related("product")

        if not order_qs.exists():
            return Response(
                {"status": "failed", "message": "No order found for this User."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(order_qs, many=True)
        return Response(
            {
                "status": "success",
                "message": "Order retrieve successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class OrderProductView(APIView):
    serializer_class = BulkProductSerializer

    def post(self, request, user_id):

        serializer = self.serializer_class(
            data={"products": request.data.get("products", []), "user_id": user_id}
        )
        serializer.is_valid(raise_exception=True)
        product_objs = serializer.save()

        return Response(
            {
                "status": "success",
                "message": "Products ordered successfully",
                "data": [ProductSerailizer(product).data for product in product_objs],
            },
            status=status.HTTP_201_CREATED,
        )
