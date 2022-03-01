from django.shortcuts import render
from .forms import RegistrationForm
from .models import Account
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
            auth.login(request,user)
            messages.success(request,"You are now logged in")

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



        
 

