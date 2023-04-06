from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from users.models import Customer, Manager, CustomerPoints, Item, Restaurant, Friendship
from users.views import CustomerPointsSerializer, ItemSerializer, RestaurantSerializer, CustomerSerializer, FriendshipSerializer
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
    restaurants = Restaurant.objects.all()
    serializer = RestaurantSerializer(restaurants, many=True)
    return Response(serializer.data, status=200)

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
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_friends(request):

    friendships = Friendship.objects.filter(customer=request.user)

    friends = [friendship.friend for friendship in friendships]
    
    serializer = CustomerSerializer(friends, many=True)
    return Response(serializer.data, status=200)