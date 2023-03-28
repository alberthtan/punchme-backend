# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, Serializer, SerializerMethodField
from users.models import Customer, Manager


class CustomerSerializer(ModelSerializer):
    token = SerializerMethodField()

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'token', 'phone_number']

class CustomerViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

class ManagerSerializer(ModelSerializer):
    token = SerializerMethodField()
    
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    class Meta:
        model = Manager
        fields = ['id', 'first_name', 'last_name', 'manager_email', 'username', 'token', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class ManagerViewSet(viewsets.ModelViewSet):
    """
    View for creating a new manager
    """
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
