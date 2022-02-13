from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.http import HttpResponse
from django.db.models import Q   #Q is QuerySet for filter search views
 

#view to display the all products or based on categories

def store(request,category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.all().filter(category = categories , is_available=True).order_by('id')
        paginator = Paginator(products,2)  #no of products to show in one page for category
        page = request.GET.get('page')
        page_products = paginator.get_page(page)

        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')   #order_by just to fix the pagination warning
        paginator = Paginator(products,6)   #no of products to show in one page all  products
        page = request.GET.get('page')
        page_products = paginator.get_page(page)

        product_count = products.count()

    context={
        'products' : page_products,
        'product_count': product_count,
    }
    return render (request,'store/store.html',context)

#view for product detail page

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


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|Q(product_name__icontains=keyword))
        products_count = products.count()
        context = {
            'products': products,
            'product_count': products_count,
        }
    return render (request,'store/store.html',context)
