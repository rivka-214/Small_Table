from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    ניהול חוות דעת בממשק האדמין.
    """

    list_display = [
        'id',
        'vendor',
        'user',
        'order',
        'rating',
        'is_public',
        'created_at',
    ]

    list_filter = [
        'is_public',
        'rating',
        'vendor',
        'created_at',
    ]

    search_fields = [
        'vendor__business_name',
        'user__username',
        'order__id',
        'comment',
        'title',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'user',
        'vendor',
        'order',
    ]

    fieldsets = (
        ('קישור', {
            'fields': ('vendor', 'user', 'order')
        }),
        ('תוכן החוות דעת', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('תצוגה', {
            'fields': ('is_public',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
