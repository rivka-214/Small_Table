from rest_framework import serializers

from .models import Package, PackageCategory, PackageCategoryItem


class PackageCategoryItemSerializer(serializers.ModelSerializer):
    """
    Serializer לפריט בקטגוריה בתוך חבילה
    """

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = PackageCategoryItem
        fields = [
            'id',
            'package_category',
            'product',
            'product_name',
            'is_premium',
            'extra_price_per_person',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PackageCategorySerializer(serializers.ModelSerializer):
    """
    Serializer לקטגוריה בתוך חבילה
    כולל את הפריטים שלה (read-only)
    """

    items = PackageCategoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = PackageCategory
        fields = [
            'id',
            'package',
            'name',
            'note',
            'min_select',
            'max_select',
            'is_active',
            'created_at',
            'updated_at',
            'items',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        ולידציה לוגית:
        - min_select לא גדול מ-max_select (אם הוגדר)
        """
        min_select = attrs.get('min_select', getattr(self.instance, 'min_select', None))
        max_select = attrs.get('max_select', getattr(self.instance, 'max_select', None))

        if max_select is not None and min_select is not None and min_select > max_select:
            raise serializers.ValidationError(
                "min_select לא יכול להיות גדול מ-max_select."
            )

        return attrs


class PackageSerializer(serializers.ModelSerializer):
    """
    Serializer לחבילה
    - מציג גם קטגוריות ופריטים (קריאה בלבד)
    - שדה vendor נלקח מהספק המחובר (בספק רגיל)
    """

    vendor_name = serializers.CharField(
        source='vendor.business_name',
        read_only=True
    )

    categories = PackageCategorySerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Package
        fields = [
            'id',
            'vendor',
            'vendor_name',
            'name',
            'description',
            'price_per_person',
            'min_guests',
            'max_guests',
            'image',
            'is_active',
            'created_at',
            'updated_at',
            'categories',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        ולידציה לוגית לחבילה:
        - min_guests לא גדול מ-max_guests (אם מוגדר)
        """
        min_guests = attrs.get('min_guests', getattr(self.instance, 'min_guests', None))
        max_guests = attrs.get('max_guests', getattr(self.instance, 'max_guests', None))

        if max_guests is not None and min_guests is not None and min_guests > max_guests:
            raise serializers.ValidationError(
                "מספר סועדים מינימלי לא יכול להיות גדול ממספר סועדים מקסימלי."
            )

        return attrs

    def create(self, validated_data):
        """
        יצירת חבילה:
        - ספק רגיל: vendor נלקח מ-request.user.vendor_profile
        - admin: יכול לשלוח vendor ידנית
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated and hasattr(user, 'vendor_profile') \
                and not (user.is_staff or user.is_superuser):
            # ספק רגיל – מכריח את ה-vendor להיות שלו
            validated_data['vendor'] = user.vendor_profile

        return super().create(validated_data)
