from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('sell/', views.sell, name='sell'),
	path('profile/', views.profile, name='profile'),
	path('cart/', views.cart, name='cart'),
	path('ordernow/', views.ordernow, name='ordernow'),
	path('paynow/', views.paynow, name='paynow'),
	path('addmoney/', views.addmoney, name='addmoney'),
	path('addaddress/', views.addaddress, name='addaddress'),
	path('product/<product_id>/', views.view_product, name='view_product'),
	path('addtocart/<product_id>/', views.addtocart, name='addtocart'),
	path('addtowish/<product_id>/', views.addtowish, name='addtowish'),
	path('deleteaddress/<address_id>/', views.deleteaddress, name='deleteaddress'),
	path('deletecartproduct/<product_id>/', views.deletecartproduct, name='deletecartproduct'),
	path('update_quantity/', views.update_quantity, name='update_quantity'),
]
