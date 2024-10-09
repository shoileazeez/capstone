from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and if they are a seller
           return request.user.is_authenticated and request.user.role == 'seller'


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and if they are a buyer
           return request.user.is_authenticated and request.user.role == 'buyer'
    
    
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user    