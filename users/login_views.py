import os, json

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.serializers import EmailField, CharField, ModelSerializer, BooleanField, SerializerMethodField
from users.models import Customer, Manager, PhoneAuthentication, EmailAuthentication, Restaurant, RestaurantQR
from users.views import CustomerSerializer, ManagerSerializer

from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from twilio_config import twilio_client, twilio_phone_number
from twilio.base.exceptions import TwilioException

class SendPhoneCodeSerializer(ModelSerializer):
    is_register = BooleanField()

    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'is_register'
        )

class SendPhoneCode(CreateAPIView):
    serializer_class = SendPhoneCodeSerializer

    def create(self, request, *args, **kwargs):
        code_request = self.serializer_class(data=request.data)
        code_request.is_valid(raise_exception=True)

        phone_number = code_request.data.get('phone_number')
        is_register = code_request.data.get("is_register")

        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()

        if phone_number is None or is_register is None:
            return Response("Missing information", status=400)
        
        customer = Customer.objects.filter(username=phone_number)

        if is_register and customer.exists():
            return Response({"error": "User already exists"}, status=400)
        elif not is_register and not customer.exists():
            return Response({"error": "User does not exist"}, status=400)
        
        if phone_number == '+13103438777':
            phone_auth = PhoneAuthentication.objects.create(
                phone_number=phone_number,
                code=123456,
            )
        else:
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

    class Meta:
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'code',
          'proxy_uuid',
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
        phone_number = verify_request.data.get("phone_number")

        try:
            user = Customer.objects.create_user(
                username=phone_number, 
                phone_number=phone_number,
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

        customer = get_object_or_404(Customer, username=phone_number)

        phone_auths = PhoneAuthentication.objects.filter(
            phone_number=phone_number,
            code=code,
        )

        if not phone_auths.exists():
            return Response(
                {
                    'code': ['Code does not match.'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                phone_auths.update(is_verified=True)
                PhoneAuthentication.objects.filter(phone_number=phone_number).delete()
        except IntegrityError:
            return Response(
                {
                    'message': 'Error verifying phone code.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        customer_serializer = CustomerSerializer(customer)
        return Response(
            {
                'message': 'Login successful.',
                'user': customer_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    
class SendEmailCodeSerializer(ModelSerializer):
    is_register = BooleanField()

    class Meta:
        model = EmailAuthentication
        fields = (
          'email',
          'is_register'
        )

class SendEmailCode(CreateAPIView):
    serializer_class = SendEmailCodeSerializer

    def create(self, request, *args, **kwargs):
        code_request = self.serializer_class(data=request.data)
        code_request.is_valid(raise_exception=True)

        email = code_request.data.get('email')
        is_register = code_request.data.get('is_register')
        
        EmailAuthentication.objects.filter(email=email).delete()

        if email is None or is_register is None:
            return Response("Missing information", status=400)
        
        manager = Manager.objects.filter(username=email)
        print(manager)

        if is_register and manager.exists():
            return Response({"error": "User already exists"}, status=400)
        elif not is_register and not manager.exists():
            return Response({"error": "User does not exist"}, status=400)
        
        if email == "alberthtan123@gmail.com" or email == "steve@pinwheelgarden.co":
            email_auth = EmailAuthentication.objects.create(
                email=email,
                code=123456,
            )
        else:
            email_auth = EmailAuthentication.objects.create(
                email=email,
            )
            while not is_register and email_auth.code == manager[0].employee_code:
                print("hello")
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
            restaurant = Restaurant.objects.create(
                name='', 
                address=json.dumps({'street_address': '', 'city': '', 'state': '', 'zip_code': ''}), 
                manager=user,
            )
            RestaurantQR.objects.create(
                restaurant=restaurant
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
    serializer_class = LoginVerifyEmailCodeSerializer

    def update(self, request, *args, **kwargs):
        verify_request = self.serializer_class(data=request.data)
        verify_request.is_valid(raise_exception=True)

        email = verify_request.data.get('email')
        code = verify_request.data.get('code')

        manager = get_object_or_404(Manager, username=email)

        email_auths = EmailAuthentication.objects.filter(
            email=email,
            code=code,
        )
        
        if not email_auths.exists():
            employee_code = str(manager.employee_code)
            if code == employee_code and employee_code != '0':
                email_auths.update(is_verified=True)
                EmailAuthentication.objects.filter(email=email).delete()
                manager_serializer = ManagerSerializer(manager)
                employee = manager_serializer.data
                employee.pop('employee_code', None)
                return Response(
                {
                    'message': 'Employee login successful.',
                    'employee': manager_serializer.data,
                },
                status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'code': ['Code does not match.'],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            with transaction.atomic():
                email_auths.update(is_verified=True)
                EmailAuthentication.objects.filter(email=email).delete()
        except IntegrityError:
            return Response(
                {
                    'message': 'Error verifying email code.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        manager_serializer = ManagerSerializer(manager)
        return Response(
            {
                'message': 'Login successful.',
                'user': manager_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
