from django.shortcuts import render,redirect
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,Payment,OrderProduct
from django.http import HttpResponse,JsonResponse
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
  

# Create your views here.


def place_order(request,total_price = 0,quantity=0):
    user = request.user
  
    
    # if the cart count is <=0 redirect back to shop

    cart_items = CartItem.objects.filter(user=user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total_price += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2*total_price)/100   # 2 % of tax on price
    grand_total = total_price + tax


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #store the billing info inside the Order Table

            data = Order()
            data.user  = user
            data.first_name = form.cleaned_data.get('first_name')
            data.last_name = form.cleaned_data.get('last_name')
            data.phone = form.cleaned_data.get('phone')
            data.email = form.cleaned_data.get('email')
            data.address_line_1 = form.cleaned_data.get('address_line_2')
            data.address_line_2 = form.cleaned_data.get('address_line_1')
            data.country = form.cleaned_data.get('country')
            data.state = form.cleaned_data.get('state')
            data.city = form.cleaned_data.get('city')
            data.order_note = form.cleaned_data.get('order_note')
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  

            #generate the order number
            year = int(datetime.date.today().strftime('%Y'))
            date = int(datetime.date.today().strftime('%d'))
            month = int(datetime.date.today().strftime('%m'))
            
            date = datetime.date(year,month,date)
            current_date = date.strftime("%Y%m%d") #20220809

            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=user,is_ordered=False,order_number=order_number)
            context = {
                'order':order,
                'cart_items': cart_items,
                'total':total_price,
                'tax':tax,
                'grand_total':grand_total,
            }


            return render(request,'orders/payments.html',context)
        else:
            print(form.errors)
            return redirect('checkout')
    else:
        context = {
                'order':order,
                'cart_items': cart_items,
                'total':total_price,
                'tax':tax,
                'grand_total':grand_total,
            }


        return render(request,'orders/payments.html',context)


def payments(request):
    body = json.loads(request.body)
    order  = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

    payment = Payment(user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
        )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    #Move the cart items to order products table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    #Reduce the quantity of sold products
        product = Product.objects.get(id = item.product_id)
        product.stock-= item.quantity
        product.save()

    #clear the cart
    CartItem.objects.filter(user=request.user).delete()

    #send order received email to user
    mail_subject = 'Congratulations !! Order Received | SuperShop'
    mail_message = render_to_string('orders/order_receieved_email.html',{
                'user': request.user,
                'order':order,
            })

    to_email = request.user.email
    send_email = EmailMessage(mail_subject,mail_message,to=[to_email])

    send_email.send()    

    #send the order number and transaction id back to sendData method via JSONResponse
    data = {
        'order_number': order.order_number,
        'transID':payment.payment_id
    }

    return JsonResponse(data)



def order_complete(request):
    order_number = request.GET.get('order_number')
    paymentID = request.GET.get('paymentID')

    print(order_number)
    print(paymentID)

    try:
        order = Order.objects.get(order_number = order_number,is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=paymentID)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
    sub_total  = 0

    for item in order_products:
        sub_total += item.product.price * item.quantity


    context = {
        'order':order,
        'order_products':order_products,
        'order_number':order_number,
        'transID':paymentID,
        'payment':payment,
        'sub_total':sub_total,

    }

    return render(request,'orders/order_complete.html',context)



            
            

