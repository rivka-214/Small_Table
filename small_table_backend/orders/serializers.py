from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem, OrderAddon
from packages.models import PackageCategoryItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    פריט הזמנה – בחירת מנה מחבילה.
    (כמו קודם, רק בלי כמות – כי הכמות היא לפי מספר סועדים)
    """

    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='package_category.name', read_only=True)
    extra_subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'package_category',
            'category_name',
            'product',
            'product_name',
            'is_premium',
            'extra_price_per_person',
            'extra_subtotal',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'is_premium',
            'extra_price_per_person',
            'extra_subtotal',
            'created_at',
        ]

    def get_extra_subtotal(self, obj):
        return obj.extra_subtotal


class OrderAddonSerializer(serializers.ModelSerializer):
    """
    תוספת בהזמנה:
    - בצד הלקוח שולחים addon + quantity.
    - השרת ממלא price_snapshot ו-subtotal.
    """

    addon_name = serializers.CharField(source='addon.name', read_only=True)
    category_name = serializers.CharField(source='addon.category.name', read_only=True)
    pricing_type = serializers.CharField(source='addon.pricing_type', read_only=True)

    class Meta:
        model = OrderAddon
        fields = [
            'id',
            'addon',
            'addon_name',
            'category_name',
            'pricing_type',
            'quantity',
            'price_snapshot',
            'subtotal',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'price_snapshot',
            'subtotal',
            'created_at',
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("כמות חייבת להיות לפחות 1.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer להזמנה:

    ביצירה:
    - קלט:
      * package (חובה)
      * guests_count
      * note (אופציונלי)
      * items: רשימת בחירות של (package_category, product)
      * addons: רשימת בחירות של (addon, quantity)
    - מחושב אוטומטית:
      * user מתוך request
      * vendor מתוך package.vendor
      * total_price לפי הפורמולה
    """

    user_name = serializers.CharField(source='user.username', read_only=True)
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)

    items = OrderItemSerializer(many=True)
    addons = OrderAddonSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_name',
            'vendor',
            'vendor_name',
            'package',
            'package_name',
            'guests_count',
            'status',
            'total_price',
            'note',
            'items',
            'addons',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'vendor',
            'total_price',
            'created_at',
        ]

    def validate_guests_count(self, value):
        if value <= 0:
            raise serializers.ValidationError("מספר הסועדים חייב להיות גדול מאפס.")
        return value

    def validate(self, attrs):
        """
        ולידציה בסיסית:
        - לא ניתן להזמין חבילה שאיננה פעילה (אם קיים is_active).
        """
        package = attrs.get('package') or getattr(self.instance, 'package', None)
        if package and hasattr(package, 'is_active') and not package.is_active:
            raise serializers.ValidationError("לא ניתן להזמין חבילה שאיננה פעילה.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        יצירת הזמנה חדשה:

        1. מוציאים מתוך הנתונים את items + addons.
        2. קובעים user מתוך request.
        3. vendor נלקח מתוך package.vendor.
        4. יוצרים Order.
        5. עבור כל item:
           - בודקים שהקטגוריה שייכת לחבילה.
           - מוצאים PackageCategoryItem.
           - שומרים is_premium + extra_price_per_person.
        6. עבור כל addon:
           - שומרים price_snapshot = addon.price.
           - subtotal מחושב במודל OrderAddon.
        7. מעדכנים total_price על בסיס הכל.
        """

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        items_data = validated_data.pop('items', [])
        addons_data = validated_data.pop('addons', [])

        package = validated_data['package']

        # קביעת הספק מהחבילה
        validated_data['vendor'] = package.vendor

        if user and user.is_authenticated:
            validated_data['user'] = user

        # יצירת ההזמנה עצמה
        order = Order.objects.create(**validated_data)

        # --- יצירת פריטי ההזמנה (מפותחות מהחבילה) ---
        for item_data in items_data:
            package_category = item_data['package_category']
            product = item_data['product']

            # ודאות שהקטגוריה שייכת לחבילה שבחרו
            if package_category.package_id != package.id:
                raise serializers.ValidationError(
                    f"קטגוריה {package_category.id} לא שייכת לחבילה שנבחרה."
                )

            try:
                pci = PackageCategoryItem.objects.get(
                    package_category=package_category,
                    product=product,
                    is_active=True,
                )
            except PackageCategoryItem.DoesNotExist:
                raise serializers.ValidationError(
                    f"המנה '{product.name}' לא זמינה בקטגוריה זו בחבילה."
                )

            OrderItem.objects.create(
                order=order,
                package_category=package_category,
                product=product,
                is_premium=pci.is_premium,
                extra_price_per_person=pci.extra_price_per_person,
            )

        # --- יצירת תוספות להזמנה (OrderAddon) ---
        for addon_data in addons_data:
            addon = addon_data['addon']
            quantity = addon_data.get('quantity', 1)

            OrderAddon.objects.create(
                order=order,
                addon=addon,
                quantity=quantity,
                price_snapshot=addon.price,
            )

        # --- חישוב סכום כולל ---
        order.update_total_price(save=True)
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        עדכון הזמנה קיימת:

        כרגע:
        - לא משנים חבילה, ספק או user.
        - אפשר לעדכן guests_count, note, status.
        - items ו-addons לא מתעדכנים כאן (אפשר להוסיף בהמשך אם תרצי).
        """

        validated_data.pop('items', None)
        validated_data.pop('addons', None)
        validated_data.pop('package', None)
        validated_data.pop('vendor', None)
        validated_data.pop('user', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        instance.update_total_price(save=True)
        return instance
