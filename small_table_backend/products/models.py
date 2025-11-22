from django.db import models
from vendors.models import VendorProfile



class Product(models.Model):
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='ספק'
    )

    product_name = models.CharField(
        max_length=200,
        verbose_name='שם המוצר'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='תיאור המוצר'
    )
# רק לשם ארגון פנימי - לא חובה למלא
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='קטגוריה',
        help_text='למשל: סלטים, מנות עיקריות, קינוחים'
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name='זמין להזמנה'
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='תמונת מוצר'
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
        verbose_name = 'מוצר'
        verbose_name_plural = 'מוצרים'
        ordering = ['-created_at']

        # אינדקסים לביצועים טובים יותר
        indexes = [
            models.Index(fields=['vendor', 'is_available']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.product_name
