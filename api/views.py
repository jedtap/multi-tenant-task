from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view

from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework import viewsets

from core.models import Tenant, CustomUser, Project, Task
from .serializers import TenantSerializer, UserSerializer, ProjectSerializer, TaskSerializer


# Function base view for Tenant model
@api_view(['POST'])
def create_tenant(request):
    serializer = TenantSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_tenants(request):
    tenants = Tenant.objects.all()
    serializer = TenantSerializer(tenants, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def edit_tenant(request, pk):
    tenant = Tenant.objects.get(pk=pk)
    serializer = TenantSerializer(tenant, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_tenant(request, pk):
    tenant = Tenant.objects.get(pk=pk)
    tenant.delete()
    return Response({'message': 'Tenant was deleted'})


# Class based view for User model
class UserListCreateView(APIView):

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            password = request.data.get('password')
            user_serializer.validated_data['password'] = make_password(password)
            
            email = request.data.get('email')
            domain = email.split('@')[1]

            try:
                tenant = Tenant.objects.get(name=domain)
            except Tenant.DoesNotExist:
                tenant_data = {'name': domain}
                tenant_serializer = TenantSerializer(data=tenant_data)
                if tenant_serializer.is_valid():
                    tenant = tenant_serializer.save()

            user_serializer.save(tenant=tenant)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateDeleteView(APIView):
    
    def put(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        password = request.data.get('password', None)
        email = request.data.get('email', None)
        if email:
            domain = email.split('@')[1]
        else:
            domain = None
        
        user_serializer = UserSerializer(user, data=request.data, partial=True)

        if user_serializer.is_valid():
            if password:
                user_serializer.validated_data['password'] = make_password(password)
            if domain:
                try:
                    tenant = Tenant.objects.get(name=domain)
                    user_serializer.save()
                except Tenant.DoesNotExist:
                    tenant_data = {'name': domain}
                    tenant_serializer = TenantSerializer(data=tenant_data)
                    if tenant_serializer.is_valid():
                        tenant = tenant_serializer.save()
                        user_serializer.save(tenant=tenant)
            else:
                user_serializer.save()
        return Response(user_serializer.data) 

    def delete(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        user.delete()
        return Response({'message': 'User was deleted'})


# Generic API view for Project model
class ProjectListCreateView(ListCreateAPIView):
	queryset = Project.objects.all()
	serializer_class = ProjectSerializer

class ProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


# View set for Task model
class TaskViewSet(viewsets.ModelViewSet):
	queryset = Task.objects.all()
	serializer_class = TaskSerializer
