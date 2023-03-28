# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, Serializer, SerializerMethodField
from users.models import Customer, Manager


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']

class CustomerViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

class ManagerSerializer(ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class ManagerViewSet(viewsets.ModelViewSet):
    """
    View for creating a new manager
    """
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
