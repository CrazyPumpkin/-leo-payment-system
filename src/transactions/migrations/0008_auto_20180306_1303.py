# Generated by Django 2.0.2 on 2018-03-06 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0007_auto_20180305_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Новая'), (1, 'Создана'), (2, 'Успешна'), (3, 'Ошибка/Возврат')], default=0),
        ),
    ]