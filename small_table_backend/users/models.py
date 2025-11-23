# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    """
    טבלת תפקידים במערכת (customer, vendor, admin וכו')
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "תפקיד"
        verbose_name_plural = "תפקידים"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    משתמש מורחב:
    - מבוסס על AbstractUser
    - מוסיף טלפון
    - קשר N-N לתפקידים דרך UserRole
    """
    phone = models.CharField(max_length=20, blank=True, null=True)

    # חשוב: זה שדה לוגי בלבד, ה-through הוא UserRole למטה
    roles = models.ManyToManyField(
        Role,
        through="UserRole",
        related_name="users",
        blank=True,
    )

    def __str__(self):
        return self.username


class UserRole(models.Model):
    """
    טבלת קישור בין Users ל-Roles
    מאפשרת:
    - למשתמש להיות עם כמה תפקידים
    - לשמור תאריך שיוך
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "שיוך תפקיד למשתמש"
        verbose_name_plural = "שיוכי תפקידים למשתמשים"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user.username} → {self.role.name}"
