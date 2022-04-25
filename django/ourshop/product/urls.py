from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('sell/', views.sell, name='sell'),
	path('product/<product_id>/', views.view_product, name='view_product'),
]
