from .models import ShoppingCartItem, ShoppingCart
from django.contrib.auth.models import AnonymousUser

def cartItemCount(request):
    if request.user.is_authenticated:
        try:
            cart = ShoppingCart.objects.get(user=request.user)
            items = ShoppingCartItem.objects.filter(cart=cart)
            count = items.count() if items else 0
        except:
            count = 0
    else:
        cart = request.session.get('cart', {})
        count = len(cart)

    return {'cart_count': count}