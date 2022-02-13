from django.db import models
from category.models import Category

from django.shortcuts import reverse
# Create your models here.


class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)  #when category is deleted all prods under category will be deleted
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse('product_detail',args=[self.category.slug, self.slug])


#this managers will allow to bring only color and sizes in the prod description to select size and color

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category = 'color',is_active=True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category = 'size',is_active=True)


variation_category_choice = (
    ('color','color'),
    ('size','size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_value = models.CharField(max_length=100,null=True)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
