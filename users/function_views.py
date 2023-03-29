
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import status
from rest_framework.response import Response

from users.models import Customer, Manager
from users.views import CustomerSerializer, ManagerSerializer


@api_view(['GET'])
@csrf_exempt
def get_customer(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)

    try:
        customer = Customer.objects.get(username=request.user)
    except Customer.DoesNotExist:
        return Response("Customer not found", status=404)
    
    user_serializer = CustomerSerializer(customer)
    return Response(user_serializer.data, status=200)


@api_view(['GET'])
@csrf_exempt
def get_manager(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)
    
    try:
        manager = Manager.objects.get(username=request.user)
    except Manager.DoesNotExist:
        return Response("Manager not found", status=404)
    
    user_serializer = ManagerSerializer(manager)
    return Response(user_serializer.data)