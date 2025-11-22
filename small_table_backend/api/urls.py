from django.urls import path, include

urlpatterns = [
    path('vendors/', include('vendors.urls')),
    path('products/', include('products.urls')),
    path('users/', include('users.urls')),
]
