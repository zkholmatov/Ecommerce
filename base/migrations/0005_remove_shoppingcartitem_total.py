# Generated by Django 5.2.4 on 2025-07-25 23:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_rename_productspecs_productspec'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcartitem',
            name='total',
        ),
    ]
