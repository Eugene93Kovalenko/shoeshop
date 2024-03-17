from django.contrib import admin
from django.utils.safestring import mark_safe

from .forms import ReviewAdminForm
from .models import *


admin.site.register(Category)
admin.site.register(ProductVariation)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Brand)
admin.site.register(Gender)
admin.site.register(Review)


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductReviewInline(admin.TabularInline):
    model = Review
    form = ReviewAdminForm
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('purchases_count', 'id')
    inlines = [ProductVariationInline, ProductImageInline, ProductReviewInline]
