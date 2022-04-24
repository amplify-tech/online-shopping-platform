from django.urls import path
from . import views

urlpatterns = [
	path('login/', views.login, name='login'),
	path('logout/', views.logout, name='logout'),
	path('register/', views.register, name='register'),
	path('loaddummy/', views.loaddummy, name='loaddummy'),
	path('startweb/', views.startweb, name='startweb'),
]
