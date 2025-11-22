from rest_framework import serializers

from .models import AddonCategory, Addon


class AddonCategorySerializer(serializers.ModelSerializer):
    """
    Serializer לקטגוריית תוספות.
    בד"כ מנוהל ע"י מנהל המערכת.
    """

    class Meta:
        model = AddonCategory
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("שם הקטגוריה חייב להכיל לפחות 2 תווים.")
        return value


class AddonSerializer(serializers.ModelSerializer):
    """
    תוספת בחבילה:
    - ספק מגדיר: package, category, name, price, pricing_type, is_included
    - לקוח רק קורא.
    """

    package_name = serializers.CharField(source='package.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Addon
        fields = [
            'id',
            'package',
            'package_name',
            'category',
            'category_name',
            'name',
            'price',
            'pricing_type',
            'is_included',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("שם התוספת חייב להכיל לפחות 2 תווים.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("מחיר התוספת לא יכול להיות שלילי.")
        return value

    def validate(self, attrs):
        """
        כאן אפשר להוסיף בעתיד:
        - בדיקה שהחבילה פעילה
        - בדיקה שהקטגוריה פעילה
        """
        return attrs
