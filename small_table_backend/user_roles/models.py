from django.db import models
from django.conf import settings
from roles.models import Role  # אם האפליקציה roles קיימת עם מודל Role

class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')  # מוודא שלא יהיה כפילות

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
