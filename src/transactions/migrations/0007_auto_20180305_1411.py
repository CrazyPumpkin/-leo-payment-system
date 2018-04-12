# Generated by Django 2.0.2 on 2018-03-05 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_auto_20180305_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='timestamp_billing',
            field=models.DateTimeField(blank=True, null=True, verbose_name='время проведения'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp_sber',
            field=models.DateTimeField(blank=True, null=True, verbose_name='время оплаты'),
        ),
    ]