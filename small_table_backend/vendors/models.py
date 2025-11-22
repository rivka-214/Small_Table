from django.db import models
from django.conf import settings


class VendorProfile(models.Model):
    """
    פרופיל ספק - מכיל את כל המידע העסקי של הספק
    """
    # קשר 1-1 עם משתמש

    # קשר למשתמש הקיים (User)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )

    # פרטים עסקיים
    business_name = models.CharField(
        max_length=200,
        verbose_name='שם העסק'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='תיאור העסק'
    )

    kashrut_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=' כשרות'
    )

    address = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='כתובת העסק'
    )

    image = models.ImageField(
        upload_to='vendors/',
        blank=True,
        null=True,
        verbose_name='תמונה/לוגו'
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name='פעיל במערכת'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='תאריך יצירה'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='תאריך עדכון'
    )

    class Meta:
        verbose_name = 'פרופיל ספק'
        verbose_name_plural = 'פרופילי ספקים'
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name