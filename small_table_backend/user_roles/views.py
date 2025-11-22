from rest_framework import viewsets
from .models import UserRole
from .serializers import UserRoleSerializer

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
