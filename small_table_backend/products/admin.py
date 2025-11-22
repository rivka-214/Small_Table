from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'product_name',
        'vendor',
        'is_available',
        'created_at'
    ]
    list_filter = ['is_available', 'vendor']
    search_fields = ['product_name', 'vendor__business_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('פרטי מוצר בסיסיים', {
            'fields': ('vendor', 'product_name', 'description')
        }),
        ('תמחור וזמינות', {
            'fields': ('base_price_per_person', 'is_available')
        }),
        ('מדיה', {
            'fields': ('image',)
        }),
        ('מידע מערכת', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']