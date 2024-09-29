from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Machine, Tool, ToolUsage, Axis, AxisData


class AddUserToGroupSerializer(serializers.Serializer):
    username = serializers.CharField()
    group = serializers.ChoiceField(choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Supervisor', 'Supervisor'), ('Operator', 'Operator')])

    def validate(self, data):
        # Check if the user exists
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        
        # Check if the group exists
        try:
            group = Group.objects.get(name=data['group'])
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist")
        
        return data

    def save(self):
        user = User.objects.get(username=self.validated_data['username'])
        group = Group.objects.get(name=self.validated_data['group'])

        user.groups.add(group)
        return user

        

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = '__all__'

class ToolUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolUsage
        fields = '__all__'

class AxisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Axis
        fields = '__all__'

class AxisDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AxisData
        fields = '__all__'


class AxisDataSerializer(serializers.ModelSerializer):
    axis_name = serializers.CharField(source='axis.axis_name', read_only=True)
    machine_id = serializers.IntegerField(source='axis.machine.machine_id', read_only=True)
    machine_name = serializers.CharField(source='axis.machine.machine_name', read_only=True)
    class Meta:
        model = AxisData
        fields = ['machine_id', 'machine_name','axis_data_id', 'axis_name', 'actual_position', 'target_position', 'distance_to_go', 'homed', 'acceleration', 'velocity', 'update_timestamp']

