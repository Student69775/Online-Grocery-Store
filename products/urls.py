from django.urls import path
from . import views
# from .views import track_order

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart),
    path('thank_you/', views.thank_you),
    path('track_order/', views.track_order, name='track_order'),   
    path('order_details/', views.order_details, name='order_details'), 
]