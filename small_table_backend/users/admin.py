from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    ממשק ניהול לפרופילי ספקים ב-Django Admin
    """

    # אילו שדות להציג ברשימה
    list_display = [
        'phone',
    ]





from django.contrib import admin

# Register your models here.
