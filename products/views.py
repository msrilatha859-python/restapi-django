from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from django.http import HttpResponse

def home(requst):
    return HttpResponse("<h1>Welcome to Brewcart API</h1>")
# GET all products & POST new product
@api_view(['GET', 'POST'])
def product_list(request):
    # GET
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # POST
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET single product, PUT update, DELETE
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # GET
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # PUT (update)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
def create_order(request):
    data = request.data

    # Validate customer details
    required_fields = [
        "full_name",
        "email",
        "phone",
        "address",
        "city",
        "pincode",
    ]

    for field in required_fields:
        if not data.get(field):
            return Response(
                {"error": f"{field} is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Validate cart items
    items = data.get("items")

    if not isinstance(items, list) or not items:
        return Response(
            {"error": "Your cart is empty or invalid."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            order_items = []
            total_amount = 0

            # Validate products and calculate total using database prices
            for item in items:
                product_id = item.get("product")
                quantity = item.get("quantity")

                if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
                    return Response(
                        {"error": "Each product must have a valid positive quantity."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                try:
                    product = Product.objects.get(pk=product_id)
                except (Product.DoesNotExist, ValueError, TypeError):
                    return Response(
                        {"error": f"Product {product_id} was not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                total_amount += product.price * quantity

                order_items.append({
                    "product": product,
                    "quantity": quantity,
                    "price": product.price,
                })

            # Create the order
            order = Order.objects.create(
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                address=data["address"],
                city=data["city"],
                pincode=data["pincode"],
                total_amount=total_amount,
            )

            # Save the products in the order
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["price"],
                )

        # Return the saved order
        serializer = OrderSerializer(order)

        return Response(
            {
                "message": "Order placed successfully!",
                "order": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception:
        return Response(
            {"error": "Unable to place your order. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )