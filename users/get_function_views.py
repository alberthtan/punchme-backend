import datetime
import jwt
import os

from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import Customer, Manager, CustomerPoints, Item, Restaurant
from users.views import CustomerPointsSerializer, ItemSerializer, RestaurantSerializer

@api_view(['GET'])
def get_customer_points(request, restaurant_id):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response("Restaurant not found.", status=404)
    
    customer_points = CustomerPoints.objects.get(customer=customer, restaurant=restaurant)
    
    serializer = CustomerPointsSerializer(customer_points)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_customer_points_list(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
    customer_points_list = CustomerPoints.objects.filter(customer=customer)
    
    serializer = CustomerPointsSerializer(customer_points_list, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_customer_points_manager_view(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)

    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    customer_points_list = CustomerPoints.objects.filter(restaurant=manager.restaurant)
    
    serializer = CustomerPointsSerializer(customer_points_list, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_items_by_restaurant(request, restaurant_id):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)
    
    items_list = Item.objects.filter(restaurant=restaurant_id)
    
    serializer = ItemSerializer(items_list, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_restaurant(request, restaurant_id):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)
    
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response("Restaurant not found", status=404)
    
    serializer = RestaurantSerializer(restaurant)
    return Response(serializer.data, status=200)

@api_view(['POST'])
def generate_ws_access_token(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials. Please log in.", status=403)
    
    payload = request.data.get("payload")
    if not payload:
        return Response("Invalid payload", status=400)

    # Set the token expiry to 15 minutes
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    # Add the expiry time to the payload
    payload["exp"] = int(expiry.timestamp())

    # Encode the JWT token using the SECRET_KEY_WS
    token = jwt.encode(payload, os.environ.get("SECRET_KEY_WS"), algorithm="HS256")

    return Response({"token": token.decode("utf-8")}, status=201)
