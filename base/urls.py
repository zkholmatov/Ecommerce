from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutPage, name='logout'),
    path('register', views.registerPage, name='register'),

    path('', views.home, name='home'),
    path('shop', views.shop, name='shop'),
    path('product-page/<str:pk>', views.productPage, name='product-page'),
    path('cart', views.cart, name='cart'),

    path('review/<str:pk>', views.addReview, name='review'),
    path('update-review/<str:pk>', views.updateReview, name='update-review'),
    path('delete-review/<str:pk>', views.deleteReview, name='delete-review'),

    path('add-to-cart/<str:product_id>', views.addToCart, name='add-to-cart'),
    path('increment-item/<str:cart_item>', views.incrementItem, name='increment-item'),
    path('decrement-item/<str:cart_item>', views.decrementItem, name='decrement-item'),
    path('delete-item/<str:cart_item>', views.deleteItem, name='delete-item'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)