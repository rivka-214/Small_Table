from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from packages.models import Package


class AddonCategory(models.Model):
    """
    Category of additions (drinks, food, waiters, etc.).
    Global for the entire system – usually managed by a system administrator.
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
    An add-on in a specific package.
    The connection to ORDER is made through the OrderAddons table (in the Orders app),
    which uses this addon and the calculate_price_for_guests() function.
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
        Calculation of the contribution of the additional price according to the number of diners:

        - fixed → fixed price per order (price)
        - per_person → price * guests_count
        """
        guests = Decimal(guests_count or 0)

        if self.pricing_type == self.PRICING_PER_PERSON:
            amount = self.price * guests
        else:
            amount = self.price

        return amount.quantize(Decimal('0.01'))
