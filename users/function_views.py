
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import status
from rest_framework.response import Response

from users.models import Customer, Manager, Item, ItemRedemption
from users.views import CustomerSerializer, ManagerSerializer, ItemSerializer, ItemRedemptionSerializer


@api_view(['GET'])
@csrf_exempt
def get_customer(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
    user_serializer = CustomerSerializer(customer)
    return Response(user_serializer.data, status=200)

@api_view(['PATCH'])
@csrf_exempt
def update_customer(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
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
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    user_serializer = ManagerSerializer(manager)
    return Response(user_serializer.data)

@api_view(['PATCH'])
@csrf_exempt
def update_manager(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
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

@api_view(['POST'])
@csrf_exempt
def create_item(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)
    
    name = request.data.get('name')
    num_points = request.data.get('num_points')

    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)

    item = Item.objects.create(
        name=name,
        num_points=num_points,
        restaurant=manager.restaurant,
    )

    item_serializer = ItemSerializer(item)
    return Response({"data": item_serializer.data}, status=201)

@api_view(['PATCH'])
@csrf_exempt
def update_item(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    item_id = request.data.get('id')

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response("Item not found", status=404)
    
    if item.restaurant.manager.username != request.user.username:
        return Response("Item does not belong to your restaurant", status=403)

    serializer = ItemSerializer(item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)
    
@api_view(['DELETE'])
@csrf_exempt
def delete_item(request, item_id):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response("Item not found", status=404)
    
    if item.restaurant.manager.username != request.user.username:
        return Response("Item does not belong to your restaurant", status=403)
    
    item.delete() 

    return Response("Item deleted successfully.", status=200)

@api_view(['POST'])
@csrf_exempt
def create_redemption(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    item_id = request.data.get('id')

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response("Item not found", status=404)

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer account not found. Please log in as a customer.", status=404)

    item_redemption = ItemRedemption.objects.create(
        customer=customer,
        item=item
    )

    serializer = ItemRedemptionSerializer(item_redemption)
    return Response({"data": serializer.data}, status=201)

@api_view(['DELETE'])
@csrf_exempt
def delete_redemption(request, redemption_id):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)

    try:
        item_redemption = ItemRedemption.objects.get(id=redemption_id)
    except ItemRedemption.DoesNotExist:
        return Response("Item Redemption not found", status=404)
    
    try:
        customer = Customer.objects.get(username=item_redemption.customer.username)
    except Customer.DoesNotExist:
        return Response("No customer associated with this item redemption", status=404)
    
    if customer.username != request.user.username:
        return Response("Item redemption does not belong to you", status=403)
    
    item_redemption.delete() 

    return Response("Item redemption deleted successfully.", status=200)
