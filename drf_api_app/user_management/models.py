from django.db import models

# Machine Model
class Machine(models.Model):
    machine_id = models.IntegerField(primary_key=True)
    machine_name = models.CharField(max_length=255, null=False)
    tool_capacity = models.IntegerField(null=False)
    
    class Meta:
        db_table = 'machine'
        managed = False

    def __str__(self):
        return self.machine_name


# Tool Model
class Tool(models.Model):
    tool_id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(Machine, related_name='tool', on_delete=models.CASCADE)
    tool_offset = models.FloatField(null=False)
    feedrate = models.FloatField(null=False)
    update_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tool'
        managed = False

    def __str__(self):
        return f"Tool {self.tool_id} for Machine {self.machine.machine_name}"


# Tool Usage Model
class ToolUsage(models.Model):
    usage_id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(Machine, related_name='tool_usage', on_delete=models.CASCADE)
    tool_in_use = models.IntegerField(null=False)
    update_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tool_usage'
        managed = False

    def __str__(self):
        return f"Tool Usage {self.usage_id} on Machine {self.machine.machine_name}"


# Axis Model
class Axis(models.Model):
    AXIS_CHOICES = [('X', 'X'), ('Y', 'Y'), ('Z', 'Z'), ('A', 'A'), ('C', 'C')]

    axis_id = models.AutoField(primary_key=True)
    machine = models.ForeignKey(Machine, related_name='axis', on_delete=models.CASCADE)
    axis_name = models.CharField(max_length=1, choices=AXIS_CHOICES, null=False)
    max_acceleration = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    max_velocity = models.DecimalField(max_digits=10, decimal_places=3, null=False)

    class Meta:
        unique_together = ('machine', 'axis_name')
        db_table = 'axis'
        managed = False

    def __str__(self):
        return f"Axis {self.axis_name} for Machine {self.machine.machine_name}"


# Axis Data Model
class AxisData(models.Model):
    axis_data_id = models.AutoField(primary_key=True)
    axis = models.ForeignKey(Axis, related_name='axis_data', on_delete=models.CASCADE)
    actual_position = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    target_position = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    distance_to_go = models.DecimalField(max_digits=10, decimal_places=3, null=False, editable=False)
    homed = models.BooleanField(null=False)
    acceleration = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    velocity = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    update_timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.distance_to_go = self.target_position - self.actual_position
        super(AxisData, self).save(*args, **kwargs)

    def __str__(self):
        return f"Axis Data for Axis {self.axis.axis_name} on Machine {self.axis.machine.machine_name}"
    
    class Meta:
        db_table = 'axis_data'
        managed = False


# Indexes
class Meta:
    indexes = [
        models.Index(fields=['axis']),
        models.Index(fields=['axis_data']),
    ]
