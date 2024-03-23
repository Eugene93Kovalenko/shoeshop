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
    fields = ('image_preview', 'image', 'is_main')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:100px; max-width:100px;" />')
        else:
            return '(No image)'

    image_preview.short_description = 'Preview'


class ProductReviewInline(admin.TabularInline):
    model = Review
    form = ReviewAdminForm
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('purchases_count', 'id')
    inlines = [ProductVariationInline, ProductImageInline, ProductReviewInline]

    # def clean(self):
    #     cleaned_data = super().clean()
    #     print(cleaned_data)
    #     images = cleaned_data.get('images')
    #     main_images_count = sum(1 for image in images.all() if image.is_main)
    #     if main_images_count != 1:
    #         raise ValidationError('Exactly one image should be marked as main image.')
