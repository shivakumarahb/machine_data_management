from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from .serializers import AddUserToGroupSerializer
from rest_framework.permissions import IsAuthenticated


from rest_framework import viewsets, permissions
from .models import Machine, Tool, ToolUsage, Axis, AxisData
from .serializers import MachineSerializer, ToolSerializer, ToolUsageSerializer, AxisSerializer, AxisDataSerializer
from django.contrib.auth.models import Group

from rest_framework import generics
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from .models import AxisData, Axis, Machine
from .serializers import AxisDataSerializer

class AddUserToGroupView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can add others to groups

    def post(self, request):
        serializer = AddUserToGroupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": f"User {user.username} added to group {request.data['group']}"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Define permissions for user groups
class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='SUPERADMIN').exists()

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Supervisor').exists()

class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Operator').exists()


# Machine ViewSet
class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperAdmin()] + [IsManager()] + [IsSupervisor()]  
        elif self.action == 'update':
            return [IsSuperAdmin()] + [IsManager()]  
        elif self.action == 'destroy':
            return [IsSuperAdmin()]  
        return super().get_permissions()

# Tool ViewSet
class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperAdmin()] + [IsManager()] + [IsSupervisor()]  
        elif self.action == 'update':
            return [IsSuperAdmin()] + [IsManager()]  
        elif self.action == 'destroy':
            return [IsSuperAdmin()]  
        return super().get_permissions()

# Tool Usage ViewSet
class ToolUsageViewSet(viewsets.ModelViewSet):
    queryset = ToolUsage.objects.all()
    serializer_class = ToolUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperAdmin()] + [IsOperator()]  
        elif self.action == 'update':
            return [IsSuperAdmin()] + [IsManager()] + [IsOperator()]  
        elif self.action == 'destroy':
            return [IsSuperAdmin()] + [IsSupervisor()]  
        return super().get_permissions()
    
# Axis ViewSet
class AxisViewSet(viewsets.ModelViewSet):
    queryset = Axis.objects.all()
    serializer_class = AxisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperAdmin()] + [IsManager()] + [IsSupervisor()]  
        elif self.action == 'update':
            return [IsSuperAdmin()] + [IsManager()]  
        elif self.action == 'destroy':
            return [IsSuperAdmin()]  
        return super().get_permissions()
    
# Axis Data ViewSet
class AxisDataViewSet(viewsets.ModelViewSet):
    queryset = AxisData.objects.all()
    serializer_class = AxisDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [IsSuperAdmin()] + [IsManager()] + [IsSupervisor()]  
        elif self.action == 'update':
            return [IsSuperAdmin()] + [IsManager()]  
        elif self.action == 'destroy':
            return [IsSuperAdmin()]  
        return super().get_permissions()



class AxisDataLast15MinutesView(generics.ListAPIView):
    serializer_class = AxisDataSerializer

    def get_queryset(self):
        machine_id = self.request.query_params.get('machine_id')
        axis_name = self.request.query_params.get('axis_name')
        axis_names = self.request.query_params.getlist('axis_name')  # If multiple axes are passed
        
        # Get the timestamp for 15 minutes ago
        time_threshold = now() - timedelta(minutes=15)
        
        # Filter based on machine_id and axis_name, and within the last 15 minutes
        queryset = AxisData.objects.filter(
            axis__machine__machine_id=machine_id,
            update_timestamp__gte=time_threshold
        )

        # If a single axis name is provided
        if axis_name:
            queryset = queryset.filter(axis__axis_name=axis_name)
        
        # If multiple axis names are provided
        if axis_names:
            queryset = queryset.filter(axis__axis_name__in=axis_names)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "No data found for the given parameters"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    
    

