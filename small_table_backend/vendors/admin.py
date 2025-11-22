from django.contrib import admin
from .models import VendorProfile
@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    """
    ממשק ניהול לפרופילי ספקים ב-Django Admin
    """
    # אילו שדות להציג ברשימה
    list_display = [
        'business_name',
        'user',
        'is_active',
        'created_at'
    ]

    # אילו שדות ניתן לחפש
    search_fields = [
        'business_name',
        'user__username',
        'user__email'
    ]
    # פילטרים בצד (סינון)
    list_filter = [
        'is_active',
        'created_at'
    ]
    # שדות לקריאה בלבד (לא ניתן לערוך)
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    # סדר השדות בטופס העריכה
    fieldsets = (
        ('מידע בסיסי', {
            'fields': ('user', 'business_name')
        }),
        ('פרטים נוספים', {
            'fields': ('description', 'kashrut_level', 'address', 'image')
        }),
        ('סטטוס', {
            'fields': ('is_active',)
        }),
        ('חותמות זמן', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # מתקפל כברירת מחדל
        }),
    )