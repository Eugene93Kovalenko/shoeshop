from django.contrib import admin
from .models import *

admin.site.register(ProductImage)
admin.site.register(ProductVariation)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Brand)
admin.site.register(Gender)
admin.site.register(Review)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
    readonly_fields = ('purchases_count', 'id')
