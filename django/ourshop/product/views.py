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
from .models import ProductImage
from .forms import ImageForm

tz = pytz.timezone('Asia/Kolkata')

###############################################################
def home(request):
    product_list = showProduct()
    context = {'product_list':product_list}
    # print(product_list)
    return render(request, 'home.html',context)
    
def sell(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/')
    seller_id = toSellerId(user.id)
    if seller_id is None:
        return redirect('/')

    if request.method == 'POST':
        print("post")
        ##################################################################
        # handle uploaded images (multiple)
        images_url_list = []
        fm = ImageForm(request.POST,request.FILES)
        files = request.FILES.getlist('multipleimages')

        if fm.is_valid():
            for f in files:
             prd_img = ProductImage(multipleimages=f)
             prd_img.save()
             images_url_list.append(prd_img.multipleimages.url)
        else:
            print("error")
            messages.info(request, "Invalid Images Uploaded!")
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