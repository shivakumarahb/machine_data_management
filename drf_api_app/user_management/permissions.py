from rest_framework.permissions import BasePermission

class CanReadWebSocketAPI(BasePermission):
    """
    Custom permission to allow 'read' access to WebSocket API for all user groups.
    """
    def has_permission(self, request, view):
        # Allow 'read' access (GET) to all groups
        if request.method == 'GET':
            return True
        return False

class CanUpdateWebSocketAPI(BasePermission):
    """
    Custom permission for update access, specific to certain user groups.
    """
    def has_permission(self, request, view):
        user = request.user
        # Allow update (PUT) for Manager and Supervisor only
        if request.method == 'PUT' and (user.groups.filter(name='Manager').exists() or 
                                        user.groups.filter(name='Supervisor').exists()):
            return True
        return False

class CanDeleteWebSocketAPI(BasePermission):
    """
    Custom permission for delete access, specific to Supervisor group.
    """
    def has_permission(self, request, view):
        user = request.user
        # Allow delete (DELETE) for Supervisor only
        if request.method == 'DELETE' and user.groups.filter(name='Supervisor').exists():
            return True
        return False
