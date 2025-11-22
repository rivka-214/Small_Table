from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from vendors.models import VendorProfile
from orders.models import Order


class Review(models.Model):
    """
    חוות דעת של לקוח על ספק, מבוססת על הזמנה קיימת.
    - רק מי שביצע הזמנה יכול להשאיר חוות דעת.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='לקוח'
    )

    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='ספק'
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='הזמנה'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name='דירוג (1-5)'
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='כותרת (אופציונלי)'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='תוכן החוות דעת'
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name='מוצג לכולם'
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
        verbose_name = 'חוות דעת'
        verbose_name_plural = 'חוות דעת'
        ordering = ['-created_at']
        # לא תהיה יותר מחוות דעת אחת לכל הזמנה
        constraints = [
            models.UniqueConstraint(
                fields=['order'],
                name='unique_review_per_order'
            )
        ]

    def __str__(self):
        return f"חוות דעת על {self.vendor.business_name} (הזמנה #{self.order_id})"
