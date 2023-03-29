import os

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, BooleanField, SerializerMethodField
from users.models import Customer, Manager, PhoneAuthentication, EmailAuthentication
from users.views import CustomerSerializer, ManagerSerializer
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from twilio_config import twilio_client, twilio_phone_number
from twilio.base.exceptions import TwilioException

class SendPhoneCodeSerializer(ModelSerializer):
    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
        )

class SendPhoneCode(CreateAPIView):
    serializer_class = SendPhoneCodeSerializer

    def create(self, request, *args, **kwargs):
        code_request = self.serializer_class(data=request.data)
        code_request.is_valid(raise_exception=True)

        phone_number = code_request.data.get('phone_number')
        
        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()
        
        phone_auth = PhoneAuthentication.objects.create(
            phone_number=phone_number,
        )
        
        try:
            twilio_client.messages.create(
                body=f"Your code for Punchme is {phone_auth.code}",
                from_=twilio_phone_number,
                to=str(phone_number),
            )
        except TwilioException as e:
            return Response({'error': 'Failed to send message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        verify_request = self.serializer_class(data=request.data)
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
        verify_request = self.serializer_class(data=request.data)
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
    
class SendEmailCodeSerializer(ModelSerializer):
    class Meta:
        model = EmailAuthentication
        fields = (
          'email',
        )

class SendEmailCode(CreateAPIView):
    serializer_class = SendEmailCodeSerializer

    def create(self, request, *args, **kwargs):
        code_request = self.serializer_class(data=request.data)
        code_request.is_valid(raise_exception=True)

        email = code_request.data.get('email')
        
        EmailAuthentication.objects.filter(email=email).delete()
        
        email_auth = EmailAuthentication.objects.create(
            email=email,
        )
        
        try:
            send_mail(
                subject="Here's your code",
                message=f"Your code for Punchme is {email_auth.code}",
                from_email=os.environ.get('EMAIL_HOST_USER'),
                recipient_list=[email_auth.email]
            )
        except Exception as e:
            # Log the error or handle it as appropriate for your application
            print(f"An error occurred while sending email: {e}")

        return Response(
            code_request.data,
            status.HTTP_201_CREATED,
        )
    
class RegisterVerifyEmailCodeSerializer(ModelSerializer):
    first_name = CharField()
    last_name = CharField()

    class Meta:
        model = EmailAuthentication
        fields = (
          'code',
          'email',
          'proxy_uuid',
          'first_name',
          'last_name',
        )

class RegisterVerifyEmailCode(UpdateAPIView):
    serializer_class = RegisterVerifyEmailCodeSerializer

    def update(self, request, *args, **kwargs):
        verify_request = self.serializer_class(data=request.data)
        verify_request.is_valid(raise_exception=True)

        email = verify_request.data.get('email')
        code = verify_request.data.get('code')
        
        email_auths = EmailAuthentication.objects.filter(
            email=email,
            code=code,
        )
        
        if not email_auths.exists():
            return Response(
                {
                    'code': ['code does not match'],
                },
                status.HTTP_400_BAD_REQUEST,                
            )
        
        email_auths.update(is_verified=True)
        EmailAuthentication.objects.filter(email=email).delete()

        # REGISTRATION
        first_name = verify_request.data.get("first_name")
        last_name = verify_request.data.get("last_name")
        email = verify_request.data.get("email")

        try:
            user = Manager.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                manager_email=email, 
                username=email, 
            )
        except IntegrityError:
            return Response(
                {
                    'detail': 'Email already registered',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_serializer = ManagerSerializer(user)

        return Response(
            {
                'detail': 'User registered successfully',
                'user': user_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    
class LoginVerifyEmailCodeSerializer(ModelSerializer):
    class Meta:
        model = EmailAuthentication
        fields = (
          'email',
          'code',
        )

class LoginVerifyEmailCode(UpdateAPIView):
    serializer_class = LoginVerifyPhoneCodeSerializer

    def update(self, request, *args, **kwargs):
        verify_request = self.serializer_class(data=request.data)
        verify_request.is_valid(raise_exception=True)

        email = verify_request.data.get('email')
        code = verify_request.data.get('code')
        
        email_auths = EmailAuthentication.objects.filter(
            email=email,
            code=code,
        )
        
        if not email_auths.exists():
            return Response(
                {
                    'code': ['code does not match'],
                },
                status.HTTP_400_BAD_REQUEST,                
            )
        
        email_auths.update(is_verified=True)
        EmailAuthentication.objects.filter(email=email).delete()

        # LOGIN
        try:
            manager = Manager.objects.get(manager_email=email)
        except ObjectDoesNotExist:
            return Response(
                {
                    'message': 'No matching user found',
                },
                status.HTTP_400_BAD_REQUEST,
            )

        manager_serializer = ManagerSerializer(manager)
        return Response(
            {
                'message': 'Login successful',
                'user': manager_serializer.data,
            },
            status.HTTP_200_OK,
        )