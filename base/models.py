from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    

class Product(models.Model):
    brand = models.CharField(max_length=30, default='')
    name = models.CharField(max_length=50)
    image = models.ImageField(default="mouse.png")
    rating = models.FloatField(default=0)
    reviews = models.IntegerField(default=0, null=True)
    price = models.FloatField(default=0)
    category = models.CharField(max_length=30)
    added_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    description = models.TextField(default='')

    def __str__(self):
        return self.brand + " " + self.name


class ProductImage(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(null=True, default="mouse.png")

    def __str__(self):
        return self.item.name + "'s product image"


class ProductSpec(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.CharField()

    def __str__(self):
        return self.item.name + " " + self.title
    

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    item = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + "'s " + self.item.name + " review"
    
    # allows 1 review per user per product
    class Meta:
        unique_together = ('user', 'item')


class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + "'s shopping cart" 

class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.cart.user.username + "'s " + self.product.name