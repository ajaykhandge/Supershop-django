from .models import Cart,CartItem
from .views import _cart_id


#context processor to return the count of quantity of items in the cart

def cart_counter(request):
    if 'admin' in request.path:
        return {}
    else:
        cart_count = 0
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            cart_items = CartItem.objects.all().filter(cart = cart[:1])

            for cart_item in cart_items:
                cart_count+=cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
        
    return dict(cart_count = cart_count)
            
