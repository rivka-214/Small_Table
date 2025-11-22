from rest_framework import serializers
from rest_framework.fields import CharField

from .models import VendorProfile


class VendorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer לפרופיל ספק
    ממיר בין VendorProfile (Python) ל-JSON (API)
    """

    # שדות נוספים לקריאה בלבד (read-only)
    username = serializers.CharField(source='user.username',read_only=True )
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            'id',
            'user',
            'username',  # מהשדה שהוספנו למעלה
            'email',  # מהשדה שהוספנו למעלה
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
        """
        וולידציה לשם העסק
        בודק שאין שם עסק זהה (case-insensitive)
        """
        # בודק אם כבר קיים עסק עם השם הזה
        # (למעט העסק הנוכחי במקרה של עדכון)
        queryset = VendorProfile.objects.filter(
            business_name__iexact=value
        )

        # אם זה עדכון (יש instance), אל תבדוק את עצמו
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk) #מוציא את העצם עצמו

        if queryset.exists():
            raise serializers.ValidationError(
                "עסק עם שם זה כבר קיים במערכת"
            )

        return value

    def validate_address(self, value):
        """
        וולידציה לשדה הכתובת
        """
        if not value or len(value) < 2:
            raise serializers.ValidationError('כתובת העסק חייבת להכיל לפחות 2 תווים.')
        if len(value) > 300:
            raise serializers.ValidationError('כתובת העסק לא יכולה להיות ארוכה מ-300 תווים.')
        return value

    def validate_description(self, value):
        """
        וולידציה לשדה תיאור העסק
        """
        if value and len(value) > 1000:
            raise serializers.ValidationError('תיאור העסק לא יכול להיות ארוך מ-1000 תווים.')
        return value

    def validate_image(self, value):
        """
        וולידציה לשדה התמונה
        """
        if value:
            valid_extensions = ['jpg', 'jpeg', 'png']
            ext = str(value.name).split('.')[-1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError('קובץ תמונה חייב להיות בפורמט jpg, jpeg או png בלבד.')
        return value

    def validate_is_active(self, value):
        """
        וולידציה לשדה is_active
        """
        if value not in [True, False]:
            raise serializers.ValidationError('ערך is_active חייב להיות True או False בלבד.')
        return value
