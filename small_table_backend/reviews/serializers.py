from rest_framework import serializers
from django.db import transaction

from .models import Review
from orders.models import Order


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer לחוות דעת:
    - ביצירה: הלקוח שולח order_id, rating, title, comment
      (user ו-vendor נגזרים מההזמנה)
    """

    user_name = serializers.CharField(source='user.username', read_only=True)
    vendor_name = serializers.CharField(source='vendor.business_name', read_only=True)
    package_name = serializers.CharField(source='order.package.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'user_name',
            'vendor',
            'vendor_name',
            'order',
            'package_name',
            'rating',
            'title',
            'comment',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'vendor',
            'user_name',
            'vendor_name',
            'package_name',
            'created_at',
            'updated_at',
        ]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("הדירוג חייב להיות בין 1 ל-5.")
        return value

    def validate_order(self, order):
        """
        בדיקה:
        - שההזמנה קיימת
        - שלא קיימת כבר חוות דעת על ההזמנה
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("משתמש לא מחובר.")

        # רק מי שביצע את ההזמנה יכול להשאיר חוות דעת
        if order.user_id != user.id:
            raise serializers.ValidationError("ניתן לכתוב חוות דעת רק על הזמנה שייכת אליך.")

        # לא לאפשר שתי חוות דעת על אותה הזמנה
        if hasattr(order, 'review') and self.instance is None:
            raise serializers.ValidationError("כבר קיימת חוות דעת להזמנה זו.")

        return order

    @transaction.atomic
    def create(self, validated_data):
        """
        יצירת חוות דעת:
        - user מתוך request
        - vendor מתוך order.vendor
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        order = validated_data['order']

        validated_data['user'] = user
        validated_data['vendor'] = order.vendor

        review = Review.objects.create(**validated_data)
        return review

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        עדכון חוות דעת קיימת (רק ע"י הלקוח או אדמין):
        - לא משנים user/vendor/order
        """
        validated_data.pop('user', None)
        validated_data.pop('vendor', None)
        validated_data.pop('order', None)

        return super().update(instance, validated_data)
