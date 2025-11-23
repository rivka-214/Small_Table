# users/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, Role, UserRole
from .serializers import UserSerializer, RoleSerializer, UserRoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    User Management:
    - JWTAuthentication
    - Enable search/sort by name, email and join date
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["username"]
    search_fields = ["username", "email"]


class RoleViewSet(viewsets.ModelViewSet):
    """
    Role Management:
    In practice – usually only an admin would touch this
    , but currently the general permission is IsAuthenticated
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name"]
    ordering = ["name"]
    search_fields = ["name", "description"]


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    Assigning roles to users:
    Other users in the code (such as Packages / Orders permissions)
    work against user.user_roles, so it is important that this model remains.
    """
    queryset = UserRole.objects.select_related("user", "role")
    serializer_class = UserRoleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["assigned_at"]
    ordering = ["-assigned_at"]
    search_fields = ["user__username", "role__name"]
