from django import forms
from .models import  ProductImage

class ImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields=['multipleimages']  
        label ={}