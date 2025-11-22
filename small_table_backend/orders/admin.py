from django.contrib import admin

from .models import Order, OrderItem
from products.models import Product
from packages.models import PackageCategory


class OrderItemInline(admin.TabularInline):
    """
    עריכת פריטי הזמנה מתוך מסך ההזמנה.
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('created_at', 'get_extra_subtotal')
    fields = (
        'package_category',
        'product',
        'is_premium',
        'extra_price_per_person',
        'get_extra_subtotal',
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        סינון דינמי:
        - package_category: רק קטגוריות של החבילה שנבחרה
        - product: אפשר לסנן לפי ספק אם רוצים (כאן פתוח לכל המוצרים)
        """
        if not hasattr(request, 'resolver_match') or not request.resolver_match:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        object_id = request.resolver_match.kwargs.get('object_id')

        if db_field.name == "package_category" and object_id:
            try:
                order = Order.objects.get(id=object_id)
                kwargs["queryset"] = PackageCategory.objects.filter(
                    package=order.package
                )
            except Order.DoesNotExist:
                pass

        if db_field.name == "product" and object_id:
            # אם רוצים להגביל למוצרים של ספק ההזמנה:
            try:
                order = Order.objects.get(id=object_id)
                kwargs["queryset"] = Product.objects.filter(
                    vendor=order.vendor
                )
            except Order.DoesNotExist:
                pass

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_extra_subtotal(self, obj):
        if obj.id:
            return f"{obj.extra_subtotal:.2f} ₪"
        return "-"

    get_extra_subtotal.short_description = 'סכום תוספת'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'vendor',
        'package',
        'guests_count',
        'status',
        'total_price',
        'created_at',
    )

    list_filter = (
        'status',
        'vendor',
        'package',
        'created_at',
    )

    search_fields = (
        'id',
        'user__username',
        'vendor__business_name',
        'package__name',
    )

    readonly_fields = ('created_at', 'total_price')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'product',
        'package_category',
        'is_premium',
        'extra_price_per_person',
        'get_extra_subtotal',
        'created_at',
    )

    list_filter = (
        'is_premium',
        'package_category',
        'created_at',
    )

    search_fields = (
        'order__id',
        'product__name',
        'order__user__username',
    )

    readonly_fields = ('created_at', 'get_extra_subtotal')

    def get_extra_subtotal(self, obj):
        return f"{obj.extra_subtotal:.2f} ₪"

    get_extra_subtotal.short_description = 'סכום תוספת'
