from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
# from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from .models import *
from datetime import datetime
import pytz
from random import randint

tz = pytz.timezone('Asia/Kolkata')
import re 
regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
# email regex

###############################################################
def check(email): 
	if(re.search(regex,email)): 
		return True 
	else: 
		return False

def verify_data(myname, myphone, mypswd1, mypswd2):
	valid=True
	mszs = []
	if len(myname) <4 or len(myname)>25 :
		valid=False
		mszs.append("fullname should be 4-25 char long.")
	if not (len(myphone) == 10 and myphone.isnumeric() ):
		valid=False
		mszs.append("phone number should be of 10 digits. ")
	if len(mypswd1) <4 or len(mypswd1)>25 :
		valid=False
		mszs.append("password should be 4-25 char long.")
	if len(mypswd2) <4 or len(mypswd2)>25 :
		valid=False
		mszs.append("password should be 4-25 char long.")
	if mypswd2 != mypswd1:
		valid=False
		mszs.append("password not match.")
	# if not check(myemail):
	# 	valid=False
	# 	mszs.append("Invalid email.")

	if User.objects.filter(username=myphone).exists():
		valid=False
		mszs.append("this phone number is already taken.")
	return valid, mszs


###############################################################
def home(request):
	return render(request, 'home.html')

def login(request):
	if request.user.is_authenticated:
		return redirect('/')
	if request.method == 'POST':
		print("login 1")
		phone = request.POST['phone_login']
		paswd = request.POST['pswd_login']
		if len(phone) != 10:
			messages.info(request, 'Invalid Phone Number')
			return redirect('/')
		elif len(paswd) <4 or len(paswd)>25:
			messages.info(request, 'Incorrect Password')
			return redirect('/')
		else:

			user = auth.authenticate(username=phone, password=paswd)
			print(user)
			if user is not None:
				auth.login(request,user)
				return redirect('/')
			else:
				messages.info(request, 'Invalid Email or Password')
				return redirect('/login/')
	else:
		return render(request, 'login.html')


def logout(request):
	user = request.user
	auth.logout(request)
	return redirect('/')


def register(request,  nvuser_id=None):
	if request.user.is_authenticated:
		return redirect('/')
	if request.method == 'POST':
		print("reg 1")
		myname  = request.POST['myname']
		myphone = request.POST['myphone']
		# myemail = request.POST['myemail']
		mypswd1 = request.POST['mypswd1']
		mypswd2 = request.POST['mypswd2']

		valid, mszs = verify_data(myname, myphone, mypswd1, mypswd2)
		print("reg 2")
		if(valid):
			new_user = User.objects.create_user(username=myphone,first_name=myname ,password=mypswd1)
			new_user.save()

			user = auth.authenticate(username=myphone, password=mypswd1)
			auth.login(request,user)
			print(user.first_name)
			return redirect('/')
		else:
			print(mszs)
			for x in mszs:
				messages.info(request, x)
			return redirect('/register/')
	else:
		return render(request, 'register.html')

