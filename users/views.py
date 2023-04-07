# users/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from users.models import Customer, Manager, Restaurant, Item, CustomerPoints, ItemRedemption, RestaurantQR, Friendship, Referral, PushToken
from users.permissions import StaffPermissions

from twilio_config import twilio_client, twilio_phone_number


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
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'token', 'phone_number', 'profile_picture']

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [StaffPermissions]

class FriendshipSerializer(ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__'

class FriendshipViewSet(viewsets.ModelViewSet):
    serializer_class = FriendshipSerializer
    queryset = Friendship.objects.all()
    permission_classes = [StaffPermissions]

class PushTokenSerializer(ModelSerializer):
    class Meta:
        model = PushToken
        fields = '__all__'

class PushTokenViewSet(viewsets.ModelViewSet):
    serializer_class = PushTokenSerializer
    queryset = PushToken.objects.all()
    permission_classes = [StaffPermissions]

class ReferralSerializer(ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'

class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    queryset = Referral.objects.all()
    permission_classes = [StaffPermissions]

class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [StaffPermissions]

class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [StaffPermissions]

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
        fields = ['id', 'first_name', 'last_name', 'manager_email', 'username', 'token', 'restaurant']

class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [StaffPermissions]

class ManagerRestaurantView(APIView):
    def post(self, request):
        manager_serializer = ManagerSerializer(data=request.data)
        restaurant_serializer = RestaurantSerializer(data=request.data.get('restaurant'))

        if manager_serializer.is_valid(raise_exception=True) and restaurant_serializer.is_valid(raise_exception=True):
            manager = manager_serializer.save()
            restaurant_serializer.save(manager=manager)

            return Response({"success": "Manager and Restaurant created successfully"}, status=status.HTTP_201_CREATED)

        return Response({"error": "Manager and Restaurant creation failed"}, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerPointsSerializer(ModelSerializer):
    class Meta:
        model = CustomerPoints
        fields = '__all__'

class CustomerPointsViewSet(viewsets.ModelViewSet):
    queryset = CustomerPoints.objects.all()
    serializer_class = CustomerPointsSerializer
    permission_classes = [StaffPermissions]

class ItemRedemptionSerializer(ModelSerializer):
    class Meta:
        model = ItemRedemption
        fields = '__all__'

class ItemRedemptionViewSet(viewsets.ModelViewSet):
    queryset = ItemRedemption.objects.all()
    serializer_class = ItemRedemptionSerializer
    permission_classes = [StaffPermissions]

class RestaurantQRSerializer(ModelSerializer):
    class Meta:
        model = RestaurantQR
        fields = '__all__'

class RestaurantQRViewSet(viewsets.ModelViewSet):
    queryset = RestaurantQR.objects.all()
    serializer_class = RestaurantQRSerializer
    permission_classes = [StaffPermissions]