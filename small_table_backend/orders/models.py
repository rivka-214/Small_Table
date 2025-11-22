from decimal import Decimal

from django.db import models
from django.conf import settings

from vendors.models import VendorProfile
from packages.models import Package, PackageCategory
from products.models import Product
from addons.models import Addon  # חשוב: חיבור לתוספות


class Order(models.Model):
    """
    הזמנה המבוססת על חבילה מוכנה בלבד.

    חישוב מחיר לפי האפיון:
    - base = package.price_per_person * guests_count
    - extras_from_items = guests_count * סכום extra_price_per_person של כל המנות המשודרגות
    - addons_total = סכום subtotal של כל התוספות שנבחרו להזמנה
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='לקוח'
    )

    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='ספק'
    )

    package = models.ForeignKey(
        Package,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='חבילה'
    )

    guests_count = models.PositiveIntegerField(
        verbose_name='מספר סועדים'
    )

    status = models.CharField(
        max_length=50,
        choices=[
            ('new', 'חדש'),
            ('processing', 'בתהליך'),
            ('completed', 'הושלם'),
            ('cancelled', 'בוטל'),
        ],
        default='new',
        verbose_name='סטטוס הזמנה'
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='סכום כולל'
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='הערות להזמנה'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='תאריך יצירה'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "הזמנה"
        verbose_name_plural = "הזמנות"

    def __str__(self):
        return f"הזמנה #{self.id} ({self.user.username})"

    def calculate_total_price(self) -> Decimal:
        """
        חישוב סכום כולל לפי האפיון:
        base = מחיר חבילה למנה * מספר סועדים
        extras_from_items = guests_count * extra_price_per_person על כל פריט משודרג
        addons_total = סכום subtotal של כל OrderAddon
        """
        if not self.package or not self.guests_count:
            return Decimal('0.00')

        guests = Decimal(self.guests_count)

        # בסיס – חבילה * מספר סועדים
        base = self.package.price_per_person * guests

        # תוספות ממנות משודרגות (אסאדו וכד')
        extras_from_items = Decimal('0.00')
        for item in self.items.all():
            extras_from_items += item.extra_price_per_person * guests

        # תוספות מהטבלת OrderAddon
        addons_total = Decimal('0.00')
        for oa in self.addons.all():  # related_name='addons'
            addons_total += oa.subtotal

        return (base + extras_from_items + addons_total).quantize(Decimal('0.01'))

    def update_total_price(self, save=True):
        """
        עדכון שדה total_price לפי המנות המשודרגות + תוספות.
        """
        self.total_price = self.calculate_total_price()
        if save:
            self.save(update_fields=['total_price'])
        return self.total_price


class OrderItem(models.Model):
    """
    פריט הזמנה – מבוסס על מוצר שנמצא בתוך קטגוריה בחבילה.
    שומר את תוספת המחיר למנה (אם משודרגת) בזמן ההזמנה.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='הזמנה'
    )

    package_category = models.ForeignKey(
        PackageCategory,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='קטגוריה בחבילה'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='מוצר'
    )

    # האם זו מנה משודרגת (כמו אסאדו)
    is_premium = models.BooleanField(
        default=False,
        verbose_name='מנה משודרגת'
    )

    # כמה תוספת למנה (לסועד אחד) בזמן ההזמנה
    extra_price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='תוספת מחיר למנה'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='תאריך יצירה'
    )

    class Meta:
        verbose_name = "פריט הזמנה"
        verbose_name_plural = "פריטי הזמנה"

    def __str__(self):
        return f"{self.product.name} (הזמנה {self.order.id})"

    @property
    def extra_subtotal(self):
        """
        כמה כסף פריט זה מוסיף להזמנה (תוספת בלבד):
        guests_count * extra_price_per_person
        """
        if not self.order or not self.order.guests_count:
            return Decimal('0.00')
        guests = Decimal(self.order.guests_count)
        return (self.extra_price_per_person * guests).quantize(Decimal('0.01'))


class OrderAddon(models.Model):
    """
    תוספת שנבחרה בהזמנה ספציפית.

    דוגמאות:
    - "שתייה קלה" – pricing_type='per_person' → price_snapshot * guests_count * quantity
    - "מלצרים" – pricing_type='fixed' → price_snapshot * quantity
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='addons',
        verbose_name='הזמנה'
    )

    addon = models.ForeignKey(
        Addon,
        on_delete=models.PROTECT,
        related_name='order_addons',
        verbose_name='תוספת'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='כמות'
    )

    # מחיר יחידה בזמן ההזמנה (מועתק מ-Addon.price)
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='מחיר יחידה בזמן ההזמנה'
    )

    # סכום כולל לתוספת הזו בהזמנה (כולל פר סועד/קבוע * כמות)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='סכום כולל לתוספת'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='תאריך יצירה'
    )

    class Meta:
        verbose_name = "תוספת בהזמנה"
        verbose_name_plural = "תוספות בהזמנה"

    def __str__(self):
        return f"{self.addon.name} (הזמנה {self.order.id})"

    def calculate_subtotal(self) -> Decimal:
        """
        מחשב subtotal לפי סוג התמחור:
        - fixed: price_snapshot * quantity
        - per_person: price_snapshot * guests_count * quantity
        """
        guests = Decimal(self.order.guests_count or 0)

        if self.addon.pricing_type == Addon.PRICING_PER_PERSON:
            base = self.price_snapshot * guests
        else:
            base = self.price_snapshot

        return (base * Decimal(self.quantity)).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        # לוודא שתמיד יש price_snapshot
        if self.price_snapshot is None:
            self.price_snapshot = self.addon.price

        # לחשב subtotal לפני שמירה
        self.subtotal = self.calculate_subtotal()
        super().save(*args, **kwargs)
