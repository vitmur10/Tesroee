from django.contrib import admin
from .models import Category, Subcategory, Product, Cart
# Register your models here.


admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(Cart)

