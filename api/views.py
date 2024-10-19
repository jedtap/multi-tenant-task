from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view

from core.models import Tenant
from .serializers import TenantSerializer


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
