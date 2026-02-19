from django.db import models
from accounts.models import VendorProfile
# Create your models here.

class Product(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True)
    sizes = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inventory = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.vendor}"

    class Meta:
        ordering = ['-created_at']



class Category(models.Model):
    title = models.CharField(max_length=200,unique=True)

    def __str__(self):
        return f"{self.title}"

class Brand(models.Model):
    title = models.CharField(max_length=200,unique=True)
    def __str__(self):
        return f"{self.title}"

class Color(models.Model):
    title = models.CharField(max_length=200,unique=True)
    def __str__(self):
        return f"{self.title}"
