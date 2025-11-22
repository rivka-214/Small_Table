from django.contrib import admin

from .models import AddonCategory, Addon


@admin.register(AddonCategory)
class AddonCategoryAdmin(admin.ModelAdmin):
    """
    ניהול קטגוריות תוספות
    """

    list_display = [
        'name',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'is_active',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('פרטי קטגוריה', {
            'fields': ('name', 'description')
        }),
        ('סטטוס', {
            'fields': ('is_active',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):
    """
    ניהול תוספות בחבילות
    """

    list_display = [
        'name',
        'package',
        'category',
        'price',
        'pricing_type',
        'is_included',
        'is_active',
        'created_at',
    ]

    list_filter = [
        'pricing_type',
        'is_included',
        'is_active',
        'package',
        'category',
        'created_at',
    ]

    search_fields = [
        'name',
        'package__name',
        'package__vendor__business_name',
        'category__name',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('קישור', {
            'fields': ('package', 'category')
        }),
        ('פרטי תוספת', {
            'fields': ('name', 'price', 'pricing_type', 'is_included')
        }),
        ('סטטוס', {
            'fields': ('is_active',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
