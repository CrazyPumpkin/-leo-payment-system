# Generated by Django 2.0.2 on 2018-03-02 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientuser',
            name='billing_userid',
            field=models.CharField(max_length=250, verbose_name='идентификатор пользователя в системе биллинга'),
        ),
    ]