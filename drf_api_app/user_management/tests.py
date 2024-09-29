from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from .models import Machine, Tool, ToolUsage, Axis, AxisData


class APITestCase(APITestCase):

    def setUp(self):
        self.superadmin_group, created = Group.objects.get_or_create(name='SUPERADMIN')
        self.manager_group, created = Group.objects.get_or_create(name='Manager')
        self.supervisor_group, created = Group.objects.get_or_create(name='Supervisor')
        self.operator_group, created = Group.objects.get_or_create(name='Operator')

        self.superadmin = User.objects.create_user(username='superadmin', password='password')
        self.manager = User.objects.create_user(username='manager', password='password')
        self.supervisor = User.objects.create_user(username='supervisor', password='password')
        self.operator = User.objects.create_user(username='operator', password='password')

        self.superadmin.groups.add(self.superadmin_group)
        self.manager.groups.add(self.manager_group)
        self.supervisor.groups.add(self.supervisor_group)
        self.operator.groups.add(self.operator_group)

    
        self.machine = Machine.objects.create(machine_name="Machine1", tool_capacity=10)  
        self.tool = Tool.objects.create(machine=self.machine, tool_offset=0.5, feedrate=100) 
        self.tool_usage = ToolUsage.objects.create(machine=self.machine, tool_in_use=self.tool.tool_id)  
        self.axis = Axis.objects.create(machine=self.machine, axis_name="X", max_acceleration=100.0, max_velocity=200.0)  
        self.axis_data = AxisData.objects.create(axis=self.axis, actual_position=50.0, target_position=100.0, homed=True, acceleration=10.0, velocity=20.0) 

    def authenticate(self, username, password):
        response = self.client.post(reverse('/o/token/'), data={
            'username': username,
            'password': password
        })
        return response.data['access']

    def test_create_machine_as_superadmin(self):
        token = self.authenticate('superadmin', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post(reverse('machine-list'), data={"machine_name": "New Machine", "tool_capacity": 15}, format='json')  
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_machine_as_manager(self):
        token = self.authenticate('manager', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post(reverse('machine-list'), data={"machine_name": "New Machine", "tool_capacity": 15}, format='json') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_machines(self):
        token = self.authenticate('superadmin', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(reverse('machine-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
