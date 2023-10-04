import json
import logging

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderElements


logger = logging.getLogger(__name__)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    payload = request.data
    
    try:
        products = payload["products"]
    except KeyError:
        return Response({"products": "Обязательное поле."}, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(products, str):
        return Response({"products": 'Ожидался list со значениями, но был получен "str"'}, status=status.HTTP_400_BAD_REQUEST)

    if products is None:
        return Response({"products": "Это поле не может быть пустым."}, status=status.HTTP_400_BAD_REQUEST)

    if isinstance(products, list) and products:
        order_obj, created = Order.objects.update_or_create(
            first_name=payload["firstname"],
            last_name=payload["lastname"],
            phone_number=payload["phonenumber"],
            address=payload["address"] 
        )
        
        for product in payload['products']:
            orderelements = OrderElements.objects.get_or_create(
                order=Order.objects.get(id=order_obj.id),
                product=Product.objects.get(id=product['product']),
                quantity=product['quantity']
            )
    else:
        return Response({"products": "Этот список не может быть пустым."}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"detail": "Метод\"GET\"не разрешен."})
