from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
# from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from datetime import datetime
import pytz,csv
from .queries import *

tz = pytz.timezone('Asia/Kolkata')
import re 
regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
# email regex

admincode_list = ['dh#io@67', 'tk$fk#48', 'dr&yh@49']
special_id = [-1, 0]

###############################################################
def check(email): 
	if(re.search(regex,email)): 
		return True 
	else: 
		return False

def verify_data(myname, myphone, mypswd1, mypswd2,myusername,myrole, admincode):
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
	if myrole not in role_dict.keys():
		valid=False
		mszs.append("Invalid User Role.")
	# if not check(myemail):
	# 	valid=False
	# 	mszs.append("Invalid email.")

	if myrole == 'a' and admincode not in admincode_list:
		valid=False
		mszs.append("Invalid Admin Code")

	if User.objects.filter(username=myusername).exists():
		valid=False
		mszs.append("this phone number is already taken.")

	return valid, mszs


###############################################################
def login(request):
	if request.user.is_authenticated:
		return redirect('/')
	if request.method == 'POST':
		phone  = request.POST['phone_login']
		paswd  = request.POST['pswd_login']
		myrole = request.POST['myrole']
		if len(phone) != 10:
			messages.info(request, 'Invalid Phone Number')
			return redirect('/login/')
		elif len(paswd) <4 or len(paswd)>25:
			messages.info(request, 'Incorrect Password')
			return redirect('/login/')
		elif myrole not in role_dict.keys():
			messages.info(request, 'Invalid User Role')
			return redirect('/login/')
		else:
			user = auth.authenticate(username=phone+myrole, password=paswd)
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
		myname  = request.POST['myname']
		myphone = request.POST['myphone']
		# myemail = request.POST['myemail']
		mypswd1 = request.POST['mypswd1']
		mypswd2 = request.POST['mypswd2']
		myrole = request.POST['myrole']
		admincode = request.POST['admincode']
		print(myname, myphone, myrole, admincode)
		myusername = myphone + myrole


		valid, mszs = verify_data(myname, myphone, mypswd1, mypswd2,myusername,myrole, admincode)
		if(valid):
			register_new_user(username=myusername,fullname=myname, role=myrole, password=mypswd1)

			user = auth.authenticate(username=myusername, password=mypswd1)
			auth.login(request,user)
			return redirect('/')
		else:
			for x in mszs:
				messages.info(request, x)
			return redirect('/register/')
	else:
		return render(request, 'register.html')


def startweb(request):
	try:
		if User.objects.filter(id=0).count() ==0:
			# register owner and admin (o,a) special_id
			new_user = User.objects.create_user(id=0,username="9999999999o",first_name="flipkart owner", last_name="o", password="jgQ#k%(gd57j")
			new_user.save()
			new_user = User.objects.create_user(id=-1,username="9999999999a",first_name="flipkart admin", last_name="a", password="jgQ#k%(gd57j")
			new_user.save()
			print("owner registered")
		# else:
		# 	print("owner already exist")

	except Exception as e:
		print(e)

	return redirect('/')

def loaddummy(request):
	if request.user.is_authenticated: 
		if request.user.id in special_id:
			try:
				clear_dbdata()
				# register other users (b,s,d)
				folder = '/home/akram/Desktop/coding/project/django/DB_part/csv_user/'
				ls = [
					[folder+'buyer.csv', 'b'],
					[folder+'seller.csv', 's'],
					[folder+'del.csv', 'd']
				]

				for filename, role in ls:
					with open(filename, 'r') as csvfile:
						reader = csv.reader(csvfile)
						column_name = next(reader)

						for row in reader:
							register_new_user(username=row[2]+role,fullname=row[1], role=role, password=row[3])

			except Exception as e:
				print(e)

	return redirect('/')
