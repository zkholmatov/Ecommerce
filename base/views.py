from django.shortcuts import render, redirect
from .models import Product, ProductImage, ProductSpec, ProductReview, ShoppingCart, ShoppingCartItem
from .forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import random
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlencode
from django.db.models import Count, Avg, FloatField, Value as V, ExpressionWrapper, F

MIN_REVIEWS = 5

# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            mergeCarts(request.user, request.session.get('cart', {}))
            # del request.session['cart']
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or passaword')

    return render(request, 'base/login.html', {})


def logoutPage(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserForm()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during regustration.')

    context = {'form': form}
    return render(request, 'base/register.html', context)


def home(request):
    featured_items = Product.objects.filter(is_featured=True)[:3]

    context = {'featured_items': featured_items}
    return render(request, 'base/home.html', context)


def shop(request):
    sort_by = request.GET.get('sort', None)
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    items = Product.objects.filter(
        Q(brand__icontains=q) |
        Q(name__icontains=q) |
        Q(category__icontains=q)
    )

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    brands = set()
    all_items = Product.objects.all()

    C = 5
    global_avg = ProductReview.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    top_rated = Product.objects.annotate(
        num_reviews=Count('productreview'),
        avg_rating=Avg('productreview__rating'),
        bayesian_rating=ExpressionWrapper(
            ((F('num_reviews') * F('avg_rating') + V(C) * V(global_avg)) / (F('num_reviews') + V(C))),
            output_field=FloatField()
        )
    ).order_by('-bayesian_rating').first()

    for item in all_items:
        brands.add(item.brand)

    if sort_by:
        items = items.order_by(sort_by)

    context = {'items': items,
               'brands': sorted(brands),
               'min_price': min_price,
               'max_price': max_price,
               'top_rated': top_rated,
               }
    return render(request, 'base/shop.html', context)


def productPage(request, pk):
    item = Product.objects.get(id=pk)
    imgs = ProductImage.objects.filter(item=pk)
    specs = ProductSpec.objects.filter(item=pk)
    similar_products = similarProducts(item)
    reviews = productReviews(item)
    reviews_total = len(reviews)

    context = {'item': item,
               'imgs': imgs,
               'specs': specs,
               'similar_products': similar_products,
               'reviews': reviews,
               'reviews_total': reviews_total,
               }
    return render(request, 'base/item_page.html', context)


def similarProducts(item):
    items = list(Product.objects.filter(category=item.category).exclude(id=item.id))

    if not items:
        return []

    sample_size = min(4, len(items))
    return random.sample(items, sample_size)


def productReviews(item):
    reviews = ProductReview.objects.filter(item=item)

    return reviews


def calculateRating(pk):
    reviews = ProductReview.objects.filter(item=pk)
    avr_rating = 0
    total_rating = 0
    for review in reviews:
        total_rating += review.rating
    
    avr_rating = total_rating/len(reviews)
    return avr_rating


@login_required(login_url='login')
def addReview(request, pk):
    form = ReviewForm()
    item = Product.objects.get(id=pk)

    if request.method == 'POST':
        review, created = ProductReview.objects.update_or_create(
            user = request.user,
            item = item,
            defaults={
                'title': request.POST.get('title'),
                'rating': request.POST.get('rating'),
                'body': request.POST.get('body'),
                'date_posted': timezone.now()
            }
        )

        if created:
            item.reviews += 1

        item.rating = calculateRating(pk)
        item.save()

        return redirect('product-page', pk)

    context = {'form': form, 'item': item}
    return render(request, 'base/review_form.html', context)


def updateReview(request, pk):
    review = ProductReview.objects.get(id=pk)
    product_id = review.item.id
    form = ReviewForm(instance=review)
    item = Product.objects.get(id=product_id)

    if request.method == 'POST':
        review.title = request.POST.get('title')
        review.rating = request.POST.get('rating')
        review.body = request.POST.get('body')
        review.save()

        item = Product.objects.get(id=product_id)
        item.rating = calculateRating(product_id)
        item.save()

        return redirect('product-page', product_id)
    
    context = {'form': form, 
               'review': review,
               'item': item,
               }
    return render(request, 'base/review_form.html', context)


def deleteReview(request, pk):
    review = ProductReview.objects.get(id=pk)
    product_id = review.item.id
    item = Product.objects.get(id=product_id)
    item.reviews -= 1
    item.save()
    review.delete()

    return redirect('product-page', product_id)


def cart(request):
    if request.user.is_authenticated:
        try:
            cart = ShoppingCart.objects.get(user=request.user)
            cart_items = cart.items.select_related('product').all()
            cart_total = 0
            item_totals = []

            for item in cart_items:
                item_totals.append(item.product.price * item.quantity)
                cart_total += item.product.price * item.quantity

            context = {'cart_items': cart_items,
                       'cart_total': cart_total,
                       'item_totals': item_totals}
            return render(request, 'base/cart.html', context)
        except ShoppingCart.DoesNotExist:
            context = {'cart_items': [],
                       'cart_total': 0}
            return render(request, 'base/cart.html', context)
        
    else:
        cart = request.session.get('cart', {})
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart_items = []
        cart_total = 0
        item_totals = []

        
        for product in products:
            quantity = cart[str(product.id)]
            item_total = product.price * quantity
            item_totals.append(item_total)
            cart_total += item_total

            cart_items.append({
                'product': product,
                'quantity': cart[str(product.id)],
            })

        context = {'cart_items': cart_items,
                   'cart_total': cart_total,
                   'item_totals': item_totals,
                }
        return render(request, 'base/cart.html', context)


def addToCart(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)

        cart_item, created = ShoppingCartItem.objects.get_or_create(
            cart = cart,
            product = product,
            defaults={'quantity': 1},
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

    else:
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1

        request.session['cart'] = cart

    return redirect('cart')


def mergeCarts(user, session_cart):
    db_cart, _ = ShoppingCart.objects.get_or_create(user=user)

    for product_id, quantity in session_cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
        except Product.DoesNotExist:
            continue

        cart_item, created = ShoppingCartItem.objects.get_or_create(
            cart=db_cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()


def incrementItem(request, cart_item):
    if request.user.is_authenticated:
        cart_item = ShoppingCartItem.objects.get(id=cart_item)
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart = request.session.get('cart', {})
        if str(cart_item) in cart:
            cart[str(cart_item)] += 1
                
        request.session['cart'] = cart

    return redirect('cart')


def decrementItem(request, cart_item):
    if request.user.is_authenticated:
        cart_item = ShoppingCartItem.objects.get(id=cart_item)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        
    else:
        cart = request.session.get('cart', {})
        if str(cart_item) in cart:
            if cart[str(cart_item)] > 1:
                cart[str(cart_item)] -= 1
            else:
                del cart[str(cart_item)]

        request.session['cart'] = cart

    return redirect('cart')


def deleteItem(request, cart_item):
    if request.user.is_authenticated:
        cart_item = ShoppingCartItem.objects.get(id=cart_item)
        cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        if str(cart_item) in cart:
            del cart[str(cart_item)]

        request.session['cart'] = cart

    return redirect('cart')