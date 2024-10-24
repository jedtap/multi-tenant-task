from django.urls import path
from . import views

from rest_framework import routers
from django.urls import include

from rest_framework.schemas import get_schema_view
from django.views.generic.base import TemplateView

router = routers.DefaultRouter()
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    path('tenants/', views.view_tenants),
    path('tenant/new/', views.create_tenant),
    path('tenant/<int:pk>/', views.edit_tenant),
    path('tenant/delete/<int:pk>/', views.delete_tenant),

    path('users/', views.UserListCreateView.as_view()),
    path('user/<int:pk>/', views.UserUpdateDeleteView.as_view()),

    path('projects/', views.ProjectListCreateView.as_view()),
    path('project/<int:pk>/', views.ProjectRetrieveUpdateDestroyView.as_view()),

    path('',include(router.urls)),

    path('login/', views.login),
    path('logout/', views.logout),

    path(r'openapi-schema', get_schema_view(
        title="Project and Task App",
        description="A multitenant application to track projects and tasks",
        version="1.0.0",
        public=True,
        ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='core/swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
        ), name='swagger-ui'),
]
