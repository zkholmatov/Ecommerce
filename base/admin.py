from django.contrib import admin

# Register your models here.
from .models import Product, ProductImage, ProductSpec, ProductReview, ShoppingCart, ShoppingCartItem

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductSpec)
admin.site.register(ProductReview)
admin.site.register(ShoppingCart)
admin.site.register(ShoppingCartItem)
