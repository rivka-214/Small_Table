from rest_framework import serializers
from rest_framework.fields import CharField

from .models import VendorProfile


class VendorProfileSerializer(serializers.ModelSerializer):
    """
    Vendor Profile Serializer
    Converts between VendorProfile (Python) and JSON (API)
    """
    username = serializers.CharField(source='user.username',read_only=True )
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            'id',
            'user',
            'username',
            'email',
            'business_name',
            'description',
            'kashrut_level',
            'address',
            'image',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [ 'id','created_at', 'is_active', 'updated_at']

    def validate_business_name(self, value):

        # בודק אם כבר קיים עסק עם השם הזה
        # (למעט העסק הנוכחי במקרה של עדכון)
        queryset = VendorProfile.objects.filter(
            business_name__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk) #מוציא את העצם עצמו

        if queryset.exists():
            raise serializers.ValidationError(
                "עסק עם שם זה כבר קיים במערכת"
            )

        return value

    def validate_address(self, value):

        if not value or len(value) < 2:
            raise serializers.ValidationError('כתובת העסק חייבת להכיל לפחות 2 תווים.')
        if len(value) > 300:
            raise serializers.ValidationError('כתובת העסק לא יכולה להיות ארוכה מ-300 תווים.')
        return value

    def validate_description(self, value):

        if value and len(value) > 1000:
            raise serializers.ValidationError('תיאור העסק לא יכול להיות ארוך מ-1000 תווים.')
        return value

    def validate_image(self, value):

        if value:
            valid_extensions = ['jpg', 'jpeg', 'png']
            ext = str(value.name).split('.')[-1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError('קובץ תמונה חייב להיות בפורמט jpg, jpeg או png בלבד.')
        return value

    def validate_is_active(self, value):

        if value not in [True, False]:
            raise serializers.ValidationError('ערך is_active חייב להיות True או False בלבד.')
        return value
