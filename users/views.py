# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, Serializer, SerializerMethodField
from users.models import Customer, Manager, Restaurant


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

class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'item1', 'item1_points', 'item2', 'item2_points', 'item3', 'item3_points']

class ManagerSerializer(ModelSerializer):
    token = SerializerMethodField()
    restaurant = RestaurantSerializer(required=True)

    def create(self, validated_data):
        restaurant_data = validated_data.pop('restaurant')
        manager = Manager.objects.create_user(**validated_data)
        Restaurant.objects.create(manager=manager, **restaurant_data)
        return manager
    
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    class Meta:
        model = Manager
        fields = ['id', 'first_name', 'last_name', 'manager_email', 'username', 'token', 'password', 'restaurant']
        extra_kwargs = {'password': {'write_only': True}}

class ManagerViewSet(viewsets.ModelViewSet):
    """
    View for creating a new manager
    """
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class ManagerRestaurantView(APIView):
    def post(self, request):
        manager_serializer = ManagerSerializer(data=request.data)
        restaurant_serializer = RestaurantSerializer(data=request.data.get('restaurant'))

        if manager_serializer.is_valid(raise_exception=True) and restaurant_serializer.is_valid(raise_exception=True):
            manager = manager_serializer.save()
            restaurant_serializer.save(manager=manager)

            return Response({"success": "Manager and Restaurant created successfully"}, status=status.HTTP_201_CREATED)

        return Response({"error": "Manager and Restaurant creation failed"}, status=status.HTTP_400_BAD_REQUEST)