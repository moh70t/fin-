from django.urls import include, path 
from .views import index, process_order, product, about, contact, add_to_cart, cart_detail, checkout, product_list, register, terms_of_service, privacy_policy,geolocalisations
from django.urls import path
from .views import process_order


   


urlpatterns = [
    path('', index, name='index'),
    # path('product/', product, name='product'),
    path('terms_of_service/', terms_of_service, name='terms_of_service'),
    path('privacy_policy/', privacy_policy, name='privacy_policy'),
    path('product_list/', product_list, name='product_list'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_detail, name='cart'),

    path('checkout/', checkout, name='checkout'),
    path('process_order/', process_order, name='process_order'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register, name='register'),
    path('geolocalisations/', geolocalisations, name='geolocalisations'),
    
     path('process_order/', process_order, name='process_order'),
]
