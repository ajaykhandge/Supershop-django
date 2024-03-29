from django.urls import path
from .import views

urlpatterns = [
    path('register/', views.register,name='register'),
    path('login/', views.login,name='login'),
    path('logout/', views.logout,name='logout'),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('', views.dashboard,name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate,name='activate'),
    path('resetpasswordvalidate/<uidb64>/<token>/', views.resetpasswordvalidate,name='resetpasswordvalidate'),
    path('forgotPassword/',views.forgotPassword, name = 'forgotPassword'),
    path('resetPassword/',views.resetPassword, name = 'resetPassword'),
    path('changePassword/',views.changePassword, name = 'changePassword'),
    path('edit_profile/',views.edit_profile, name = 'edit_profile'),

    #orders
    path('my_orders/',views.my_orders, name = 'my_orders'),
    path('order_details/<int:order_id>/',views.order_details, name = 'order_details'),
   
    

    




     
  
]


 