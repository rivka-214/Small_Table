from django.contrib import admin

from .models import Package, PackageCategory, PackageCategoryItem


class PackageCategoryItemInline(admin.TabularInline):
    """
    אינליין לפריטים בקטגוריה בתוך חבילה
    """
    model = PackageCategoryItem
    extra = 1
    autocomplete_fields = ['product']
    fields = [
        'product',
        'is_premium',
        'extra_price_per_person',
        'is_active',
        'created_at',
        'updated_at',
    ]
    readonly_fields = ['created_at', 'updated_at']


class PackageCategoryInline(admin.StackedInline):
    """
    אינליין לקטגוריות חבילה בתוך חבילה
    """
    model = PackageCategory
    extra = 1
    fields = [
        'name',
        'note',
        'min_select',
        'max_select',
        'is_active',
        'created_at',
        'updated_at',
    ]
    readonly_fields = ['created_at', 'updated_at']
    show_change_link = True


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    """
    ממשק ניהול לחבילות
    """

    list_display = [
        'name',
        'vendor',
        'price_per_person',
        'min_guests',
        'max_guests',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'is_active',
        'vendor',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
        'vendor__business_name',
        'vendor__user__username',
        'vendor__user__email',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('פרטי חבילה', {
            'fields': ('vendor', 'name', 'description', 'image')
        }),
        ('תמחור וסועדים', {
            'fields': ('price_per_person', 'min_guests', 'max_guests')
        }),
        ('סטטוס', {
            'fields': ('is_active',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [PackageCategoryInline]


@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    """
    ניהול קטגוריות חבילה
    """

    list_display = [
        'name',
        'package',
        'min_select',
        'max_select',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'is_active',
        'package',
        'created_at',
    ]

    search_fields = [
        'name',
        'package__name',
        'package__vendor__business_name',
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('פרטי קטגוריה', {
            'fields': ('package', 'name', 'note')
        }),
        ('מגבלות בחירה', {
            'fields': ('min_select', 'max_select')
        }),
        ('סטטוס', {
            'fields': ('is_active',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [PackageCategoryItemInline]


@admin.register(PackageCategoryItem)
class PackageCategoryItemAdmin(admin.ModelAdmin):
    """
    ניהול פריטים בקטגוריות חבילה
    """

    list_display = [
        'product',
        'package_category',
        'is_premium',
        'extra_price_per_person',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'is_active',
        'is_premium',
        'package_category__package',
        'package_category',
    ]

    search_fields = [
        'product__name',
        'package_category__name',
        'package_category__package__name',
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('קישור', {
            'fields': ('package_category', 'product')
        }),
        ('מאפייני תמחור', {
            'fields': ('is_premium', 'extra_price_per_person')
        }),
        ('סטטוס', {
            'fields': ('is_active',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
