from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from packages.models import Package


class AddonCategory(models.Model):
    """
    קטגוריית תוספות (שתייה, חד"פ, מלצרים וכו').
    גלובלית לכל המערכת – בד"כ מנוהלת ע"י מנהל מערכת.
    """

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='שם קטגוריית תוספת'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='תיאור כללי'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='פעילה'
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
        verbose_name = 'קטגוריית תוספת'
        verbose_name_plural = 'קטגוריות תוספות'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Addon(models.Model):
    """
    תוספת בחבילה מסוימת.

    דוגמאות:
    - "שתייה קלה" – מחיר פר סועד
    - "מלצרים" – מחיר קבוע להזמנה
    - "חד"פ יוקרתי" – פר סועד

    החיבור ל-ORDER מתבצע דרך טבלת OrderAddons (באפליקציית ההזמנות),
    שמשתמשת ב-addon הזה ובפונקציה calculate_price_for_guests().
    """

    PRICING_FIXED = 'fixed'
    PRICING_PER_PERSON = 'per_person'

    PRICING_TYPE_CHOICES = [
        (PRICING_FIXED, 'קבוע להזמנה'),
        (PRICING_PER_PERSON, 'לפי סועד'),
    ]

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='addons',
        verbose_name='חבילה'
    )

    category = models.ForeignKey(
        AddonCategory,
        on_delete=models.PROTECT,
        related_name='addons',
        verbose_name='קטגוריית תוספת'
    )

    name = models.CharField(
        max_length=150,
        verbose_name='שם התוספת'
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='מחיר תוספת'
    )

    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_TYPE_CHOICES,
        default=PRICING_FIXED,
        verbose_name='סוג תמחור'
    )

    is_included = models.BooleanField(
        default=False,
        verbose_name='כלול כברירת מחדל בחבילה'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='זמינה להזמנה'
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
        verbose_name = 'תוספת בחבילה'
        verbose_name_plural = 'תוספות בחבילות'
        ordering = ['package', 'category', 'name']
        unique_together = ('package', 'name')

    def __str__(self) -> str:
        return f"{self.name} ({self.package.name})"

    def calculate_price_for_guests(self, guests_count: int) -> Decimal:
        """
        חישוב תרומת התוספת למחיר לפי מספר סועדים:

        - fixed       → מחיר קבוע להזמנה (price)
        - per_person  → price * guests_count
        """
        guests = Decimal(guests_count or 0)

        if self.pricing_type == self.PRICING_PER_PERSON:
            amount = self.price * guests
        else:
            amount = self.price

        return amount.quantize(Decimal('0.01'))
