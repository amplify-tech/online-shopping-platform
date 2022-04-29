from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from datetime import datetime
import pytz,csv
from .queries import *
from .models import ImageModel
from .forms import ImageForm

tz = pytz.timezone('Asia/Kolkata')

###############################################################
def home(request):
    product_list = showProduct()
    context = {'product_list':product_list}
    # print(product_list)
    return render(request, 'home.html',context)

def view_product(request, product_id=None):
    if not product_id.isnumeric():
        return HttpResponse("<h1> invalid url </h1>")
    product_data,product_photo = getProduct(product_id)
    if product_data is None:
        return HttpResponse("<h1> invalid url </h1>")
    context = {'product_data':product_data, 'product_photo':product_photo}
    return render(request, 'view_product.html',context)

def profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/')

    wallet_data = getWallet(user.id)
    address_data = None
    isbuyer = (user.username)[-1]=='b'
    if isbuyer:
        address_data = getAddress(user.id)
    context = {'wallet_data':wallet_data, 'address_data':address_data, 'isbuyer':isbuyer}
    return render(request, 'profile.html',context)

def cart(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/')
    if user.username[-1] !='b':   # check if buyer
        return redirect('/')

    product_data = getCart(user.id)
    total_price = sum(x.price*x.quantity for x in product_data)
    if len(product_data) ==0:
        messages.info(request, "Your Cart is empty!")
    context = {'product_data':product_data, 'total_price':total_price}
    return render(request, 'cart.html',context)

def ordernow(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/')
    if user.username[-1] !='b':   # check if buyer
        return redirect('/')
  
    product_data = getCart(user.id)
    print(product_data)
    if len(product_data) ==0:
        messages.info(request, "please add some products to Cart")
        return redirect('/cart/')

    address_data = getAddress(user.id)
    wallet_data = getWallet(user.id)
    total_price = sum(x.price*x.quantity for x in product_data)
    context = {'product_data':product_data, 'total_price':total_price, 
        'address_data':address_data,'wallet_data':wallet_data}
    return render(request, 'ordernow.html',context)

def paynow(request):
    user = request.user
    if user.is_authenticated and request.method == 'POST':
        if user.username[-1] !='b':   # check if buyer
            return redirect('/')
        address_id  = request.POST['address_id']
        if address_id.isnumeric():
            msz = payNow(user.id, address_id)
            messages.info(request, msz)
        else:
            messages.info(request, "Invalid Input!")

    return redirect('/')


def addmoney(request):
    user = request.user
    if user.is_authenticated and request.method == 'POST':
        amount  = request.POST['amount']
        if amount.isnumeric():
            result = addWalletMoney(user.id, amount)
            if result:
                messages.info(request, "Money Added")
            else:
                messages.info(request, "Something went wrong : Money not added!!")
        else:
            messages.info(request, "Invalid Input!")
    return redirect('/profile/')
    
def addaddress(request):
    user = request.user
    if user.is_authenticated and request.method == 'POST':
        if user.username[-1] !='b':   # check if buyer
            return redirect('/')
        state  = request.POST['state']
        city  = request.POST['city']
        street  = request.POST['street']
        pincode  = request.POST['pincode']
        msz = addaddressDB(user.id, state, city, street,pincode)
        messages.info(request, msz)
    return redirect('/profile/')

def deleteaddress(request,address_id=None):
    user = request.user
    if user.is_authenticated:
        result = deleteaddressDB(user.id,address_id)
        if result:
            messages.info(request, "Address Deleted")
        else:
            messages.info(request, "Something went wrong : Address not Deleted!!")
    return redirect('/profile/')

def addtocart(request, product_id=None):
    if not product_id.isnumeric():
        return HttpResponse("<h1> invalid url </h1>")
    user = request.user
    if user.is_authenticated:
        result = addtoCart(user.id,product_id)
        if result:
            messages.info(request, "Product Added to Cart")
        else:
            messages.info(request, "Something went wrong : Product not added!!")
    else:
        messages.info(request, "Please Login as Buyer First!")
    return redirect('/cart/')

def deletecartproduct(request, product_id=None):
    if not product_id.isnumeric():
        return HttpResponse("<h1> invalid url </h1>")
    user = request.user
    if not user.is_authenticated:
        return redirect('/')
    if user.username[-1] !='b':   # check if buyer
        return redirect('/')

    result = deleteFromCart(user.id,product_id)
    if result:
        messages.info(request, "Product Deleted from Cart")
    else:
        messages.info(request, "Something went wrong : Product not deleted!!")
    return redirect('/cart/')

def update_quantity(request):
    user = request.user
    if user.is_authenticated and request.method == 'POST':
        if user.username[-1] !='b':   # check if buyer
            return redirect('/')

        product_id  = request.POST['product_id']
        quantity  = request.POST['quantity']
        result = updateQuantity(user.id,product_id,quantity)
        if result:
            messages.info(request, "Quantity updated")
        else:
            messages.info(request, "Something went wrong : Quantity Not updated!!")
    return redirect('/cart/')

def addtowish(request, product_id=None):
    if not product_id.isnumeric():
        return HttpResponse("<h1> invalid url </h1>")
    user = request.user
    if user.is_authenticated:
        result = addtoWish(user.id,product_id)
        if result:
            messages.info(request, "Product Added to Wishlist")
        else:
            messages.info(request, "Something went wrong : Product not added!!")
    else:
        messages.info(request, "Please Login as Buyer First!")
    return redirect('/cart/')

##################################################################
def sell(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/')
    seller_id = toSellerId(user.id)
    if seller_id is None:
        return redirect('/')

    if request.method == 'POST':
        ##################################################################
        # handle uploaded images (multiple)
        images_url_list = []
        fm = ImageForm(request.POST,request.FILES)
        files = request.FILES.getlist('multipleimages')
        if len(files) ==0:
            messages.info(request, "Images Required!")
            return redirect('/sell/')

        if fm.is_valid():
            for f in files:
             prd_img = ImageModel(multipleimages=f)
             prd_img.save()
             images_url_list.append(prd_img.multipleimages.url)
        else:
            print("error")
            messages.info(request, "Invalid Images Uploaded!")
            return redirect('/sell/')
        ##################################################################
        
        product_name  = request.POST['product_name']
        product_price  = request.POST['product_price']
        product_detail  = request.POST['product_detail']

        result = addProduct(seller_id,product_name, product_price, product_detail,images_url_list)

        if result:
            messages.info(request, "product added")
        else:
            messages.info(request, "Something went wrong : product not added!")
        return redirect('/sell/')
    else:
        return render(request, 'seller/sell.html')

