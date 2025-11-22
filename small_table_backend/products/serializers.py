from rest_framework import serializers
from .models import Product
from vendors.models import VendorProfile


class ProductSerializer(serializers.ModelSerializer):
    """
    ממיר בין אובייקט Product (פייתון) ל-JSON (API)
    """
    vendor = serializers.PrimaryKeyRelatedField(queryset=VendorProfile.objects.all())
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'vendor',
            'vendor_name',
            'product_name',
            'description',
            'category',
            'is_available',
            'image',
            'created_at',
            'updated_at',
        ]

    def validate_product_name(self, value):
        if not value or len(value) < 2:
            raise serializers.ValidationError('שם מוצר חייב להכיל לפחות 2 תווים.')
        if len(value) > 200:
            raise serializers.ValidationError('שם מוצר לא יכול להיות ארוך מ-200 תווים.')
        return value

    def validate_base_price_per_person(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('מחיר למנה חייב להיות גדול מ-0.')
        return value

    def validate_category(self, value):
        if not value or len(value) < 2:
            raise serializers.ValidationError('קטגוריה חייבת להכיל לפחות 2 תווים.')
        if len(value) > 100:
            raise serializers.ValidationError('קטגוריה לא יכולה להיות ארוכה מ-100 תווים.')
        return value
