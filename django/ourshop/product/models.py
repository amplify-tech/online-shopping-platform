from django.db import models

class ProductImage(models.Model):
    multipleimages = models.ImageField(upload_to='product_images',blank=True,null=True)