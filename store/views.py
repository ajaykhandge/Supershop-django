from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,ReviewRating,ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.http import HttpResponse
from django.db.models import Q   #Q is QuerySet for filter search views
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct


 

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
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user = request.user,product__id = product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # create the reviews 
    reviews = ReviewRating.objects.filter(product__id = product.id,status=True)
    #product gallery

    product_gallery = ProductGallery.objects.filter(product_id=product.id)

        

    context = {
        'reviews':reviews,
        'orderproduct' :orderproduct,
        'product': product,
        'product_in_cart': product_in_cart,
        'product_gallery':product_gallery,
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


def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER') #current product page url
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            form = ReviewForm(request.POST,instance = review)   #update review if present
            form.save()
            messages.success(request,'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thank you! Your review has been recorded.')
                return redirect(url)

