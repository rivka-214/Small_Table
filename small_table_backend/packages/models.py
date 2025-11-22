from django.db import models
from django.core.validators import MinValueValidator
from vendors.models import VendorProfile
from products.models import Product


class Package(models.Model):
    """
    חבילה שספק מציע ללקוחות
    לדוגמה: בסיסית / קלאסית / יוקרתית
    """

    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.PROTECT,
        related_name='packages',
        verbose_name='ספק'
    )

    name = models.CharField(
        max_length=150,
        verbose_name='שם החבילה'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='תיאור החבילה'
    )

    price_per_person = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='מחיר למנה'
    )

    min_guests = models.PositiveIntegerField(
        default=1,
        verbose_name='מספר סועדים מינימלי'
    )

    max_guests = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='מספר סועדים מקסימלי'
    )

    image = models.ImageField(
        upload_to='packages/',
        blank=True,
        null=True,
        verbose_name='תמונה מייצגת'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='פעילה להזמנה'
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
        verbose_name = 'חבילה'
        verbose_name_plural = 'חבילות'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.vendor.business_name})"


class PackageCategory(models.Model):
    """
    קטגוריה בתוך חבילה
    לדוגמה: סלטים, מנות עיקריות, קינוחים
    """

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='חבילה'
    )

    name = models.CharField(
        max_length=150,
        verbose_name='שם הקטגוריה'
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name='הערות'
    )

    min_select = models.PositiveIntegerField(
        default=0,
        verbose_name='מינימום לבחירה'
    )

    max_select = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='מקסימום לבחירה'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='פעילה להזמנה'
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
        verbose_name = 'קטגוריה בחבילה'
        verbose_name_plural = 'קטגוריות בחבילות'
        ordering = ['id']
        unique_together = ('package', 'name')

    def __str__(self):
        return f"{self.name} - {self.package.name}"


class PackageCategoryItem(models.Model):
    """
    פריט (מנה) בקטגוריה בתוך חבילה
    מחבר בין Product לבין PackageCategory
    """

    package_category = models.ForeignKey(
        PackageCategory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='קטגוריה'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='package_items',
        verbose_name='מוצר'
    )

    is_premium = models.BooleanField(
        default=False,
        verbose_name='מנה משודרגת'
    )

    extra_price_per_person = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='תוספת מחיר למנה'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='זמין להזמנה'
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
        verbose_name = 'פריט בחבילת קטגוריה'
        verbose_name_plural = 'פריטים בחבילת קטגוריה'
        ordering = ['id']
        unique_together = ('package_category', 'product')

    def __str__(self):
        return f"{self.product.name} ({self.package_category.name})"
