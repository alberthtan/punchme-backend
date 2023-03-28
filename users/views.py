# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, Serializer, SerializerMethodField
from users.models import Customer, Manager, Restaurant, CustomerPoints, PhoneAuthentication

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
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'token', 'phone_number']

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'item1', 'item1_points', 'item2', 'item2_points', 'item3', 'item3_points']

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

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
    
class CustomerPointsSerializer(ModelSerializer):
    class Meta:
        model = CustomerPoints
        fields = ['id', 'customer', 'restaurant', 'num_points']

class CustomerPointsViewSet(viewsets.ModelViewSet):
    queryset = CustomerPoints.objects.all()
    serializer_class = CustomerPointsSerializer

class SendPhoneCodeSerializer(ModelSerializer):
    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
        )

class SendPhoneCode(CreateAPIView):
    serializer_class = SendPhoneCodeSerializer

    def create(self, request, *args, **kwargs):
        code_request = SendPhoneCodeSerializer(data=request.data)
        code_request.is_valid(raise_exception=True)

        phone_number = code_request.data.get('phone_number')
        
        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()
        
        phone_auth = PhoneAuthentication.objects.create(
            phone_number=phone_number,
        )
        
        twilio_client.messages.create(
            body=f"Your code for Punchme is {phone_auth.code}",
            from_=twilio_phone_number,
            to=str(phone_number),
        )

        return Response(
            code_request.data,
            status.HTTP_201_CREATED,
        )


class VerifyPhoneCodeSerializer(ModelSerializer):
    # username = CharField()
    email = EmailField()
    first_name = CharField()
    last_name = CharField()

    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'code',
          'proxy_uuid',
          'last_name',
          'email',
          'first_name'
        )

class VerifyPhoneCode(UpdateAPIView):
    serializer_class = VerifyPhoneCodeSerializer

    def update(self, request, *args, **kwargs):
        verify_request = VerifyPhoneCodeSerializer(data=request.data)
        verify_request.is_valid(raise_exception=True)

        phone_number = verify_request.data.get('phone_number')
        code = verify_request.data.get('code')
        
        phone_auths = PhoneAuthentication.objects.filter(
            phone_number=phone_number,
            code=code,
        )
        
        if not phone_auths.exists():
            return Response(
                {
                    'code': ['code does not match'],
                },
                status.HTTP_400_BAD_REQUEST,                
            )
        
        phone_auths.update(is_verified=True)

        # # if not is_registration, then it's a login
        # # so return serialized user in the response

        # first_name = verify_request.data.get("first_name")
        # last_name = verify_request.data.get("last_name")
        # email = verify_request.data.get("email")

        # user = Customer.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=(email + '_CUSTOMER'), phone_number=phone_number)
        # user_serializer = CustomerSerializer(user)
        return Response(
            # user_serializer.data,
            {"success": True},
            status.HTTP_200_OK,
        )