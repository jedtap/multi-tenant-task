from django.urls import path
from . import views


urlpatterns = [
    path('tenants/', views.view_tenants),
    path('tenant/new/', views.create_tenant),
    path('tenant/<int:pk>/', views.edit_tenant),
    path('tenant/delete/<int:pk>/', views.delete_tenant),
]
