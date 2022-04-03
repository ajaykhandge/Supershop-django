from django.urls import path
from .import views

urlpatterns = [
    path('', views.carts,name='carts'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_cart_item,name = 'remove_cart_item'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.remove_cart,name = 'remove_cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name = 'add_cart'),
    path('checkout/',views.checkout, name = 'checkout'),
 
     
    
]