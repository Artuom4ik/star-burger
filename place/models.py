from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(max_length=200, verbose_name="Адрес места", unique=True)
    latitude = models.FloatField(verbose_name="Широта", null=True)
    longitude = models.FloatField(verbose_name="Долгота", null=True)
    update_at = models.DateTimeField('Время запроса к геокодеру', default=timezone.now)

    def __str__(self) -> str:
        return self.address
