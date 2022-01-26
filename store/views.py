from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
 



def store(request,category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.all().filter(category = categories , is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context={
        'products' : products,
        'product_count': product_count,
    }
    return render (request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        product_in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = product).exists()
        
         
    except Exception as e:
        raise e

    context = {
        'product': product,
        'product_in_cart': product_in_cart,
    }

    return render(request,'store/product_detail.html',context)
