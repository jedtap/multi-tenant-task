from rest_framework import serializers
from core.models import Tenant, CustomUser, Project, Task

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'password', 'is_staff', 'is_admin', 'tenant', 'username']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
