# Generated by Django 3.2.15 on 2023-10-24 10:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20231008_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderelements',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
    ]
