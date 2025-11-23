# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    """
    System Role Table (customer, vendor, admin, etc.)
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
    Extended User:
    - Based on AbstractUser
    - Adds phone
    - N-N relationship to roles via UserRole
    """
    phone = models.CharField(max_length=20, blank=True, null=True)

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
    A link table between Users and Roles
    allows:
    - A user to have multiple roles
    - Save an association date
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
