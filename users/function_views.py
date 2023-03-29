
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

@api_view(['PATCH'])
@csrf_exempt
def update_customer(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    customer = request.user
    serializer = CustomerSerializer(customer, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Extract the validated data from the serializer
    validated_data = serializer.validated_data

    # Update the customer instance with the validated data
    for attr, value in validated_data.items():
        setattr(customer, attr, value)

    # Save the customer instance
    customer.save()

    # Retrieve the updated customer instance from the database
    instance = Customer.objects.get(id=customer.id)

    # Serialize the updated customer instance and return the response
    serializer = CustomerSerializer(instance)
    return Response({"user": serializer.data}, status=200)

@api_view(['DELETE'])
@csrf_exempt
def delete_customer(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)
    
    customer = request.user
    customer.delete()
    return Response("Customer deleted successfully.", status=200)

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

@api_view(['PATCH'])
@csrf_exempt
def update_manager(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    manager = request.user
    serializer = ManagerSerializer(manager, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Extract the validated data from the serializer
    validated_data = serializer.validated_data

    # Update the manager instance with the validated data
    for attr, value in validated_data.items():
        if attr == "restaurant":
            for restaurant_attr, restaurant_value in value.items():
                setattr(manager.restaurant, restaurant_attr, restaurant_value)
        else:
            setattr(manager, attr, value)

    # Save the manager instance
    manager.save()

    # Retrieve the updated manager instance from the database
    instance = Manager.objects.get(id=manager.id)

    # Serialize the updated manager instance and return the response
    serializer = ManagerSerializer(instance)
    return Response({"user": serializer.data}, status=200)

@api_view(['DELETE'])
@csrf_exempt
def delete_manager(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)
    
    manager = request.user
    manager.delete()
    return Response("Manager deleted successfully.", status=200)