from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
#private function with _

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
    
#function to increment the item to cart

def add_cart(request,product_id):
    current_user = request.user
    #get the product and its variation

    product = Product.objects.get(id = product_id)

    #if the current user is authenticated 
    if current_user.is_authenticated:
        product_variation = []  #empty list to store the variation value of cart item 

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        

        #get and Add the item to the cart

        is_cart_item_exists = CartItem.objects.filter(product=product,user = current_user).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product,user = current_user)

            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

         


            if product_variation in existing_variation_list:
                #since the product_variation is already there only increase the cart quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item  = CartItem.objects.get(product=product,id = item_id)
                item.quantity+=1
                item.save()
            else:
                #create the cart item with new variation
                item = CartItem.objects.create(product=product,quantity=1,user = current_user)
                if len(product_variation) > 0:
                    item.variations.clear()   #clear the variation if added before
                    item.variations.add(*product_variation)   #* to add all variations
                item.save()
        
        else:
            cart_item = CartItem.objects.create(
                product = product,
                user = current_user,
                quantity = 1,)

            if len(product_variation) > 0:
                cart_item.variations.clear()    #clear the variation if added before 
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('carts')
    
    #if the user is not authenticated
    else:
        product_variation = []  #empty list to store the variation value of cart item 

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        #get the cart 
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        #get and Add the item to the cart

        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart)

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product,cart = cart)

            #get the current and existing variations
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            print(existing_variation_list)


            if product_variation in existing_variation_list:
                #since the product_variation is already there only increase the cart quantity
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item  = CartItem.objects.get(product=product,id = item_id)
                item.quantity+=1
                item.save()
            else:
                #create the cart item with new variation
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()   #clear the variation if added before
                    item.variations.add(*product_variation)   #* to add all variations
                item.save()
        
        else:
            cart_item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity = 1,)

            if len(product_variation) > 0:
                cart_item.variations.clear()    #clear the variation if added before 
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('carts')

#function to decrement the variation of item from cart and cart_item_id is variation of cart_item

def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id = product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user = request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart = cart,id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    
    return redirect( 'carts')


#function to delete the item from cart 

def remove_cart_item(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id = product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product, user = request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = product, cart = cart,id=cart_item_id)

    #no need to check for non availabity since if is visible in cart then it will be available
    cart_item.delete()

    return redirect('carts')

    
def carts(request,total_price = 0,quantity=0,cart_items = None):
    try:
        tax = 0
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active=True)

        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2*total_price)/100   # 2 % of tax on price
        grand_total = total_price + tax

    except ObjectDoesNotExist:
        pass #ignore for now

    context = {
        'total_price': total_price,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax': tax,
        'grand_total' : grand_total,
    }


    return render(request,'store/cart.html',context)

@login_required(login_url='login')
def checkout(request,total_price = 0,quantity=0,cart_items = None):
    try:
        tax = 0
        grand_total = 0
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active=True)

        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2*total_price)/100   # 2 % of tax on price
        grand_total = total_price + tax

    except ObjectDoesNotExist:
        pass #ignore for now

    context = {
        'total_price': total_price,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax': tax,
        'grand_total' : grand_total,
    }

    return render(request,'store/checkout.html',context)



