# Generated by Django 3.2.9 on 2021-11-08 10:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('musicshop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата получени заказа'),
        ),
    ]