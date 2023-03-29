# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, BooleanField, SerializerMethodField
from users.models import Customer, Manager, Restaurant, CustomerPoints, PhoneAuthentication
from users.views import CustomerSerializer
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from twilio_config import twilio_client, twilio_phone_number

class SendPhoneCodeSerializer(ModelSerializer):
    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
        )

class SendPhoneCode(CreateAPIView):
    serializer_class = SendPhoneCodeSerializer

    def create(self, request, *args, **kwargs):
        print("here1")
        code_request = SendPhoneCodeSerializer(data=request.data)
        code_request.is_valid(raise_exception=True)

        phone_number = code_request.data.get('phone_number')
        
        print("here")
        print(phone_number)
        print(PhoneAuthentication.objects.all())
        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()
        
        phone_auth = PhoneAuthentication.objects.create(
            phone_number=phone_number,
        )
        print(PhoneAuthentication.objects.all())
        print(PhoneAuthentication.objects.filter(phone_number=phone_number))
        
        twilio_client.messages.create(
            body=f"Your code for Punchme is {phone_auth.code}",
            from_=twilio_phone_number,
            to=str(phone_number),
        )

        return Response(
            code_request.data,
            status.HTTP_201_CREATED,
        )


class RegisterVerifyPhoneCodeSerializer(ModelSerializer):
    first_name = CharField()
    last_name = CharField()
    email = EmailField()

    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'code',
          'email',
          'proxy_uuid',
          'first_name',
          'last_name',
        )

class RegisterVerifyPhoneCode(UpdateAPIView):
    serializer_class = RegisterVerifyPhoneCodeSerializer

    def update(self, request, *args, **kwargs):
        verify_request = RegisterVerifyPhoneCodeSerializer(data=request.data)
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
        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()

        # REGISTRATION
        first_name = verify_request.data.get("first_name")
        last_name = verify_request.data.get("last_name")
        email = verify_request.data.get("email")
        phone_number = verify_request.data.get("phone_number")

        try:
            user = Customer.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                username=phone_number, 
                phone_number=phone_number
            )
        except IntegrityError:
            return Response(
                {
                    'detail': 'Phone number already registered',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_serializer = CustomerSerializer(user)

        return Response(
            {
                'detail': 'User registered successfully',
                'user': user_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    

class LoginVerifyPhoneCodeSerializer(ModelSerializer):
    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'code',
        )

class LoginVerifyPhoneCode(UpdateAPIView):
    serializer_class = LoginVerifyPhoneCodeSerializer

    def update(self, request, *args, **kwargs):
        verify_request = LoginVerifyPhoneCodeSerializer(data=request.data)
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
        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()

        # LOGIN
        try:
            customer = Customer.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            return Response(
                {
                    'message': 'No matching user found',
                },
                status.HTTP_400_BAD_REQUEST,
            )

        customer_serializer = CustomerSerializer(customer)
        return Response(
            {
                'message': 'Login successful',
                'user': customer_serializer.data,
            },
            status.HTTP_200_OK,
        )