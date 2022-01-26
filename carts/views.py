from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from .models import Cart,CartItem

#private function with _

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
    
#function to increment the item to cart

def add_cart(request,product_id):
    product = Product.objects.get(id = product_id)
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    #Add the item to the cart

    try:
        cart_item = CartItem.objects.get(product = product,cart = cart)
        cart_item.quantity+=1
        cart_item.save()
    
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1,)
        cart_item.save()

    return redirect('carts')

#function to decrement the item from cart

def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cart_item = CartItem.objects.get(product = product, cart = cart)

     

    if cart_item.quantity > 1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect( 'carts')


#function to delete the item from cart 

def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cart_item = CartItem.objects.get(product = product, cart = cart)

    #no need to check for non availabity since if is visible in cart then it will be available
    cart_item.delete()

    return redirect('carts')

     
    



def carts(request,total_price = 0,quantity=0,cart_items = None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart,is_active=True)

        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2*total_price)/100   # 2 % of tax on price
        grand_total = total_price + tax

    except:
        pass #ignore for now

    context = {
        'total_price': total_price,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax': tax,
        'grand_total' : grand_total,
    }


    return render(request,'store/cart.html',context)



