from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Prefetch
from collections import defaultdict

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_available_restaurants(self):
        restaurants = defaultdict(set)
        for restaurant_menu_item in RestaurantMenuItem.objects.filter(availability=True).select_related('restaurant', 'product'):
            restaurants[restaurant_menu_item.restaurant].add(restaurant_menu_item.product)

        for order in self:
            order_restaurants = []
            products = {order_elements.product for order_elements in 
                        order.order_products.select_related('product')}

            for restaurant, restaurant_products in restaurants.items():
                if products.issubset(restaurant_products):
                    order_restaurants.append(restaurant)

            order.restaurants = order_restaurants
        return self


class Order(models.Model):
    ORDER_STATUS = (
        ('Unprocessed', 'Необработанный'),
        ('Preparing', 'Готовится'),
        ('Delivered', 'Доставляется'),
        ('Completed', 'Выполнен')
    )

    PAYMENT_METHOD = (
        ('In cash', 'Наличностью'),
        ('Electronically', 'Электронно')
    )

    firstname = models.CharField(max_length=100, verbose_name="Имя")
    lastname = models.CharField(max_length=100, verbose_name="Фамилия")
    phonenumber = PhoneNumberField(region="RU", verbose_name="Номер телефона")
    address = models.CharField(max_length=200, verbose_name="Адрес доставки")
    status = models.CharField(max_length=100, choices=ORDER_STATUS, db_index=True, verbose_name='Статус заказа', default='Unprocessed')
    comment = models.TextField('Комментарий', max_length=200, blank=True)
    registrated_at = models.DateTimeField(db_index=True, blank=True, default=timezone.now, verbose_name="Дата создания")
    called_at = models.DateTimeField(db_index=True, blank=True, null=True, verbose_name="Дата звонка")
    delivered_at = models.DateTimeField(db_index=True, blank=True, null=True, verbose_name="Дата доставки")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, db_index=True, verbose_name="Способ оплаты", default="")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, blank=True, null=True, related_name='orders', verbose_name='Ресторан')

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"
    


class OrderElements(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_products",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_elements", verbose_name="Продукт")
    quantity = models.IntegerField(verbose_name="Количество")
    cost = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Стоимость", default=0)

    def __str__(self):
        return f"{self.product} {self.order}"

        
