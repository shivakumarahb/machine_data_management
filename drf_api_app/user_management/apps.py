from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_management'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)

def create_default_groups(sender, **kwargs):  
    from django.contrib.auth.models import Group 
    groups = ['Admin', 'Manager', 'Supervisor', 'Operator']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)
