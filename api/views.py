from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view

from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework import viewsets

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.middleware.csrf import get_token
from rest_framework.authtoken.models import Token

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import BasePermission

from core.models import Tenant, CustomUser, Project, Task
from .serializers import TenantSerializer, UserSerializer, ProjectSerializer, TaskSerializer


# Login and Logout
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(username=email, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        django_login(request, user)
        csrf_token = get_token(request)
        return Response({'token': token.key, 'user': user.email, 'csrf_token': csrf_token})
    else:
        return Response("oops, user and/or password is not valid", status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def logout(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        django_logout(request) 
    except Token.DoesNotExist:
        return Response({"error": "oops, your not logged in"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


# Function base view for Tenant model
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_tenant(request):
    if request.user.is_admin:
        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "oops, your not an admin to see this"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def view_tenants(request):
    if request.user.is_admin:
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)
    else:
        return Response({"error": "oops, your not an admin to see this"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def edit_tenant(request, pk):
    if request.user.is_admin:
        tenant = Tenant.objects.get(pk=pk)
        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    else:
        return Response({"error": "oops, your not an admin to see this"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_tenant(request, pk):
    if request.user.is_admin:
        tenant = Tenant.objects.get(pk=pk)
        tenant.delete()
        return Response({'message': 'Tenant was deleted'})
    else:
        return Response({"error": "oops, your not an admin to see this"}, status=status.HTTP_401_UNAUTHORIZED)


# Class based view for User model
class UserListCreateView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        if request.user.is_admin:
            users = CustomUser.objects.all()
        else:
            users = CustomUser.objects.filter(tenant=request.user.tenant)

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

            user_serializer.save(tenant=tenant, username=email)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateDeleteView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.is_admin:
            pass
        elif pk == request.user.id:
            pass
        else:
            return Response({"error": "Unauthorized to make changes"}, status=status.HTTP_401_UNAUTHORIZED)
 
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
        if not request.user.is_admin:
            return Response({"error": "Unauthorized to delete a user"}, status=status.HTTP_401_UNAUTHORIZED)
 
        user = CustomUser.objects.get(pk=pk)
        user.delete()
        return Response({'message': 'User was deleted'})


# Custom Permissions
class IsTenant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.tenant == obj.tenant
    
class IsStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
    
class IsPartOfProject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all()

class IsPartOfTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj.project
        return request.user in project.users.all()


# Generic API view for Project model
class ProjectListCreateView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTenant]

    def get_queryset(self):
        return Project.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        tenant = self.request.user.tenant
        user = self.request.user
        project = serializer.save(tenant=tenant)
        project.users.add(user)

class ProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTenant, IsPartOfProject]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data

        if 'users' in data:
            new_users = data['users']
            for user_id in new_users:
                if not instance.users.filter(id=user_id).exists():
                    instance.users.add(user_id)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

# View set for Task model
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTenant, IsPartOfTask]

    def get_queryset(self):
        return Task.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        tenant = self.request.user.tenant
        serializer.save(tenant=tenant)
