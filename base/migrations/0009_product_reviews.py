# Generated by Django 5.2.4 on 2025-07-27 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_remove_product_description_product_brand_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reviews',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
