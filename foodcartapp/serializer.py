from rest_framework.serializers import ModelSerializer
from phonenumber_field.serializerfields import PhoneNumberField

from .models import OrderElements, Order


class OrderElementsSerializer(ModelSerializer):
    class Meta:
        model = OrderElements
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderElementsSerializer(many=True, allow_empty=False)
    phonenumber = PhoneNumberField()

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'address']
