import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.db.models import FloatField
from django.db.models.functions import Cast
from django.contrib.gis.geos import Point, Distance

from users.models import Customer, Manager, CustomerPoints, Item, Restaurant, Friendship, PushToken, Transaction
from users.views import CustomerPointsSerializer, ItemSerializer, RestaurantSerializer, CustomerSerializer, PushTokenSerializer, TransactionSerializer
from users.permissions import CustomerPermissions, ManagerPermissions, IsAuthenticatedAndActive

@api_view(['GET'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_customer_points(request, restaurant_id):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response("Restaurant not found.", status=404)
    
    try:
        customer_points = CustomerPoints.objects.get(customer=customer, restaurant=restaurant)
    except CustomerPoints.DoesNotExist:
        return Response("Customer does not have points at this restaurant", status=404)
    
    serializer = CustomerPointsSerializer(customer_points)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_customer_points_list(request):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
    customer_points_list = CustomerPoints.objects.filter(customer=customer)
    
    serializer = CustomerPointsSerializer(customer_points_list, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def get_customer_points_manager_view(request):
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    customer_points_list = CustomerPoints.objects.filter(restaurant=manager.restaurant)
    
    serializer = CustomerPointsSerializer(customer_points_list, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndActive])
def get_items_by_restaurant(request, restaurant_id):
    items_list = Item.objects.filter(restaurant=restaurant_id)
    
    serializer = ItemSerializer(items_list, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndActive])
def get_restaurant(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except Restaurant.DoesNotExist:
        return Response("Restaurant not found", status=404)
    
    serializer = RestaurantSerializer(restaurant)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_all_restaurants(request):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer", status=404)
    
    restaurants = Restaurant.objects.all()

    customer_points = CustomerPoints.objects.filter(customer=customer)
    restaurants = [restaurant for restaurant in restaurants if restaurant not in [point.restaurant for point in customer_points]]
            
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data, status=200)

@api_view(['POST'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_restaurants_by_location(request):
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if not latitude or not longitude:
        return Response('Missing information', status=400)
    
    # geolocator = Nominatim(user_agent='PunchmeManager')
    # location = geolocator.reverse(f"{latitude}, {longitude}")
    # city = location.raw['address'].get('city')
    
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer", status=404)
    
    # Convert user's latitude and longitude to a Point object
    user_location = Point(latitude, longitude)

    # Filter restaurants within a certain radius (in this example, 5 kilometers)
    radius = 5  # in kilometers
    restaurants = Restaurant.objects.filter(
        address__distance_lte=(user_location, Distance(km=radius))
    )

    # Calculate the distance between each restaurant and the user's location
    for restaurant in restaurants:
        restaurant_latitude, restaurant_longitude = get_lat_long_from_address(restaurant.address)
        restaurant_location = Point(restaurant_longitude, restaurant_latitude)
        distance_in_km = geodesic(user_location, restaurant_location).km

        # Add the distance to the restaurant object as a computed field
        restaurant.distance = distance_in_km

    # Sort the restaurants by distance
    restaurants = sorted(restaurants, key=lambda r: r.distance)
    
    # restaurants = Restaurant.objects.filter(address__contains=f'"city":"{city}"')

    customer_points = CustomerPoints.objects.filter(customer=customer)
    restaurants = [restaurant for restaurant in restaurants if restaurant not in [point.restaurant for point in customer_points]]
            
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data, status=200)

def get_lat_long_from_address(address):
    # Parse the address and extract the latitude and longitude
    geolocator = Nominatim(user_agent='PunchmeManager')

    location = geolocator.geocode(f"{address['street_address']}, {address['city']}, {address['state']} {address['zip_code']}")

    latitude = location.latitude
    longitude = location.longitude

    return latitude, longitude

@api_view(['GET'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def get_customer_manager_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response("Customer not found", status=404)
    
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager", status=404)
    
    try:
        CustomerPoints.objects.get(customer=customer, restaurant=manager.restaurant)
    except CustomerPoints.DoesNotExist:
        return Response("Customer does not have data with your restaurant", status=404)
    
    serializer = CustomerSerializer(customer)
    data = serializer.data.copy()
    data.pop('token', None)
    return Response(data, status=200)

@api_view(['GET'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def get_transactions_by_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response("Customer not found", status=404)
    
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager", status=404)
    
    transactions = Transaction.objects.filter(restaurant=manager.restaurant)
    customer_transactions = []

    for transaction in transactions:
        transaction_customer_id = json.loads(transaction.customer_string)['id']
        if transaction_customer_id == customer_id:
            customer_transactions.append(transaction)

    serializer = TransactionSerializer(customer_transactions, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_friends(request):

    friendships = Friendship.objects.filter(customer=request.user)

    friends = [friendship.friend for friendship in friendships]
    
    serializer = CustomerSerializer(friends, many=True)
    data = serializer.data.copy()
    
    for friend in data:
        friend.pop('token', None)
    
    return Response(data, status=200)

@api_view(['GET'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_push_tokens(request, phone_number):

    try:
        customer = Customer.objects.get(username=phone_number)
    except Customer.DoesNotExist:
        return Response("Customer not found.", status=400)

    push_tokens = PushToken.objects.filter(customer=customer)
    
    serializer = PushTokenSerializer(push_tokens, many=True)
    data = serializer.data.copy()
    
    return Response(data, status=200)

@api_view(['POST'])
def dummy(request):
    path = request.data.get("path")
    initial = request.data.get("initial_url")
    query = request.data.get("query_params")
    print("initial url")
    print(initial)
    print("path")
    print(path)
    print("query params")
    print(query)
    return Response(status=200)
