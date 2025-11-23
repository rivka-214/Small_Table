from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem, OrderAddon
from packages.models import PackageCategoryItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Order item – choosing a dish from a package.
    (As before, only without quantity – because the quantity is according to the number of diners)
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
    Add-on to order:
    - On the client side, addon + quantity is sent.
    - The server fills in price_snapshot and subtotal.
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
    Serializer Oreder:
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

        package = attrs.get('package') or getattr(self.instance, 'package', None)
        if package and hasattr(package, 'is_active') and not package.is_active:
            raise serializers.ValidationError("לא ניתן להזמין חבילה שאיננה פעילה.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        items_data = validated_data.pop('items', [])
        addons_data = validated_data.pop('addons', [])

        package = validated_data['package']


        validated_data['vendor'] = package.vendor

        if user and user.is_authenticated:
            validated_data['user'] = user


        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            package_category = item_data['package_category']
            product = item_data['product']

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

        for addon_data in addons_data:
            addon = addon_data['addon']
            quantity = addon_data.get('quantity', 1)

            OrderAddon.objects.create(
                order=order,
                addon=addon,
                quantity=quantity,
                price_snapshot=addon.price,
            )

        order.update_total_price(save=True)
        return order

    @transaction.atomic
    def update(self, instance, validated_data):

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
