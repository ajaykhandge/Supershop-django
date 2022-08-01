from django.shortcuts import render
from .forms import RegistrationForm
from .models import Account
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.contrib import messages,auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#verfication email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests



# Create your views here.

def register(request):
    if request.method == 'POST':
        form =RegistrationForm(request.POST)   #fetch all data of form POST request
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            #create the user 
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,username = username,email=email,password=password)
            user.phone_number = phone_number
            user.save()

            #User activation with the expirable email link
            current_site = get_current_site(request)
            mail_subject = 'Activate your SuperShop Account'
            mail_message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),   #encoding user id with base 64 encryption
                'token': default_token_generator.make_token(user),

            })

            to_email = email
            send_email = EmailMessage(mail_subject,mail_message,to=[to_email])

            send_email.send()    #send the activation email 
            #messages.success(request,'Thank you registration with us. We have sent verification email to your email address. Please verify your email address.')
            return redirect('/accounts/login/?command=verification&email='+email)
            

    else:
        form = RegistrationForm()
        print('In the GET Section')

    context={
        'form':form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)
        if user is not None:

            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    #get the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #get the cart items from user to access product variations
                    cart_item = CartItem.objects.filter(user = user) 

                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    
                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity+= 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item  in cart_item:
                                item.user = user
                                item.save()
                        
            except:
                pass
            auth.login(request,user)
            messages.success(request,"You are now logged in.")
            
            #checkout=/cart/checkout/           <--- url
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))   #{'checkout': '/cart/checkout/'}
                
                if 'checkout' in params:
                    nextPage  = params['checkout']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')

            
        else:
            messages.error(request,'Invalid login creditinals')
            return redirect('login')

    return render(request,'accounts/login.html')

@login_required(login_url ='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'you are successfully logout!!')
    return redirect('login')


def activate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()   #deocode the encoded uid
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations !! You account is successfully activated')
        return redirect('dashboard')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):

    return render(request,'accounts/dashboard.html')


def forgotPassword(request):
    if request.method =='POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact = email)

            #Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset your Password | SuperShop '
            mail_message = render_to_string('accounts/forgot_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),   #encoding user id with base 64 encryption
                'token': default_token_generator.make_token(user),

            })

            to_email = email
            send_email = EmailMessage(mail_subject,mail_message,to=[to_email])

            send_email.send()    #send the activation email 
            messages.success(request,'Password reset email has been sent to your account!')
            return redirect('login')


            
        
        else:
            messages.error(request,'Account Does not exist!')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotpassword.html')



def resetpasswordvalidate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()   #deocode the encoded uid
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid       #store the uid in session to access it later for reseting password
        messages.success(request,'Please reset your password.')
        return redirect('resetPassword')

    else:
        messages.error(request,'The Link has been expired :(')
        return redirect('login')


def resetPassword(request):
    if request.method =='POST':
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']

        if password == confirmpassword:
            #get the uid saved in session to access user account
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)

            user.set_password(password)
            user.save()
            messages.success(request,'Password reset sucessfully!! Login now :)')
            return redirect('login')

        else:
            messages.error(request,'Password Does not match')
            return redirect('resetPassword')
    return render(request,'accounts/resetpassword.html')




        
 

