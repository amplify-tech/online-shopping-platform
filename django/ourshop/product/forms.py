from django import forms
from .models import  ImageModel

class ImageForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields=['multipleimages']  
        label ={}