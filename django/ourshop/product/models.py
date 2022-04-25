from django.db import models

class ImageModel(models.Model):
    multipleimages = models.ImageField(upload_to='product_images',blank=True,null=True)