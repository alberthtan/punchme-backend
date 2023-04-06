import datetime, jwt, uuid, os
from datetime import timedelta
from uuid import uuid4

from rest_framework.decorators import api_view

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.dispatch import receiver
from django.utils import timezone

from users.models import Customer, Manager, Item, ItemRedemption, RestaurantQR, CustomerPoints
from users.models import Friendship, Restaurant, restaurant_signal
from users.views import CustomerSerializer, ManagerSerializer, ItemSerializer, RestaurantSerializer
from users.views import ItemRedemptionSerializer, RestaurantQRSerializer, FriendshipSerializer
from users.permissions import CustomerPermissions, ManagerPermissions, IsAuthenticatedAndActive

from twilio_config import twilio_client, twilio_phone_number
from twilio.base.exceptions import TwilioException

@receiver(restaurant_signal)
def restaurant_signal_receiver(sender, restaurant_id, **kwargs):
    generate_new_qr_code(sender)

@api_view(['GET'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def get_customer(request):
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)
    
    user_serializer = CustomerSerializer(customer)
    return Response(user_serializer.data, status=200)

@api_view(['PATCH'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def update_customer(request):
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
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def delete_customer(request): 
    customer = request.user
    customer.delete()
    return Response("Customer deleted successfully.", status=200)

@api_view(['GET'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def get_manager(request):
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    user_serializer = ManagerSerializer(manager)
    return Response(user_serializer.data)

@api_view(['PATCH'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def update_manager(request):
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
            # Save the updated restaurant object
            manager.restaurant.save()
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
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def delete_manager(request):
    manager = request.user
    manager.delete()
    return Response("Manager deleted successfully.", status=200)

@api_view(['PATCH'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def update_restaurant(request):
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    try:
        restaurant = Restaurant.objects.get(id=manager.restaurant.id)
    except Restaurant.DoesNotExist:
        return Response("Restaurant not found.", status=404)
    
    serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Extract the validated data from the serializer
    validated_data = serializer.validated_data

    # Update the customer instance with the validated data
    for attr, value in validated_data.items():
        print(attr)
        print(value)
        setattr(restaurant, attr, value)

    # Save the customer instance
    restaurant.save()

    # Retrieve the updated customer instance from the database
    instance = Restaurant.objects.get(id=restaurant.id)

    # Serialize the updated customer instance and return the response
    serializer = RestaurantSerializer(instance)
    return Response({"restaurant": serializer.data}, status=200)

@api_view(['POST'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def create_item(request):
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
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def update_item(request):
    item_id = request.data.get('item_id')

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response("Item not found", status=404)
    
    if item.restaurant.manager.username != request.user.username:
        return Response("Invalid. Please log in as the manager of this restaurant.", status=403)

    serializer = ItemSerializer(item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)
    
@api_view(['DELETE'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def delete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response("Item not found", status=404)
    
    if item.restaurant.manager.username != request.user.username:
        return Response("Invalid. Please log in as the manager of this restaurant.", status=403)
    
    item.delete() 

    return Response("Item deleted successfully.", status=200)

@api_view(['POST'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def create_redemption(request):
    item_id = request.data.get('item_id')

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer account not found. Please log in as a customer.", status=404)

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response("Item not found", status=404)
    
    # Check if customer has enough points
    try:
        customer_points = CustomerPoints.objects.get(restaurant=item.restaurant, customer=customer)
        if customer_points.num_points < item.num_points:
            return Response("You do not have enough points.", status=404)
    except CustomerPoints.DoesNotExist:
        return Response("You do not have enough points.", status=404)

    item_redemption = ItemRedemption.objects.create(
        customer=customer,
        item=item
    )

    serializer = ItemRedemptionSerializer(item_redemption)
    return Response({"data": serializer.data}, status=201)

@api_view(['DELETE'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def delete_redemption(request, redemption_id):
    try:
        item_redemption = ItemRedemption.objects.get(id=redemption_id)
    except ItemRedemption.DoesNotExist:
        return Response("Item Redemption not found", status=404)
    
    try:
        customer = Customer.objects.get(username=item_redemption.customer.username)
    except Customer.DoesNotExist:
        return Response("No customer associated with this item redemption", status=404)
    
    if customer.username != request.user.username:
        return Response("Invalid. Please log in as a customer who owns this redemption.", status=403)
    
    item_redemption.delete() 

    return Response("Item redemption deleted successfully.", status=200)

def generate_new_qr_code(restaurant):
    try:
        restaurant_qr = RestaurantQR.objects.get(restaurant=restaurant)
        new_code = uuid4()
        restaurant_qr.code = new_code
        restaurant_qr.default_qr = str(new_code) + '|https://apps.apple.com/app/punchme/id6447275121'
        restaurant_qr.save()
    except RestaurantQR.DoesNotExist:
        restaurant_qr = RestaurantQR(restaurant=restaurant, code=uuid4())
        restaurant_qr.save()

    return restaurant_qr

@api_view(['PATCH'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def generate_qr(request): 
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    restaurant_qr = generate_new_qr_code(manager.restaurant)
    serializer = RestaurantQRSerializer(restaurant_qr)
    return Response(serializer.data, status=200)
    
@api_view(['GET'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def get_qr(request): 
    try:
        manager = Manager.objects.get(username=request.user.username)
    except Manager.DoesNotExist:
        return Response("Manager not found. Please log in as a manager.", status=404)
    
    try:
        restaurant_qr = RestaurantQR.objects.get(restaurant=manager.restaurant)
        serializer = RestaurantQRSerializer(restaurant_qr)
        return Response(serializer.data, status=200)
    except RestaurantQR.DoesNotExist:
        return Response("Restaurant QR does not exist.", status=404)

@api_view(['PATCH'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def award_point(request):
    code = request.data.get('code')

    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("Customer not found. Please log in as a customer.", status=404)

    try:
        uuid.UUID(code)  # Check if code is a valid UUID
    except ValueError:
        return Response("Invalid QR code format.", status=400)

    try:
        restaurant_qr = RestaurantQR.objects.get(code=code)
    except RestaurantQR.DoesNotExist:
        return Response("Invalid QR. Please generate another.", status=404)
    
    restaurant = restaurant_qr.restaurant
    
    try:
        customer_points = CustomerPoints.objects.get(restaurant=restaurant, customer=customer)
        # time_elapsed = timezone.now() - customer_points.timestamp
        # if time_elapsed < timedelta(minutes=10):
        #     return Response("You can only earn one point every 10 minutes.", status=400)
        customer_points.num_points += 1
        customer_points.timestamp = timezone.now()  # Set timestamp to current time
        customer_points.save()
    except CustomerPoints.DoesNotExist:
        customer_points = CustomerPoints(customer=customer, restaurant=restaurant, num_points=1, timestamp=timezone.now())
        customer_points.save()

    restaurant_signal.send(sender=restaurant, restaurant_id=restaurant.id)

    return Response({"message": "Point awarded successfully.",
                     "restaurant_id": restaurant.id}, status=200)

@api_view(['PATCH'])
@permission_classes([ManagerPermissions, IsAuthenticatedAndActive])
def validate_redemption(request):
    code = request.data.get('code')

    try:
        uuid.UUID(code)  # Check if code is a valid UUID
    except ValueError:
        return Response("Invalid QR code format.", status=400)

    try:
        item_redemption = ItemRedemption.objects.get(code=code)
    except ItemRedemption.DoesNotExist:
        return Response("Invalid redemption.", status=404)

    if item_redemption.item.restaurant.manager.username != request.user.username:
        return Response("Invalid. Please log in as the manager of this restaurant.", status=403)
    
    num_points = item_redemption.item.num_points
    restaurant = item_redemption.item.restaurant
    customer = item_redemption.customer
    
    # Use customer points
    try:
        customer_points = CustomerPoints.objects.get(restaurant=restaurant, customer=customer)
        if customer_points.num_points >= num_points:
            customer_points.num_points -= num_points
            customer_points.save()
        else:
            return Response("Customer does not have enough points.", status=400)
    except CustomerPoints.DoesNotExist:
        return Response("Customer does not have enough points.", status=400)
    
    # Delete item redemption object
    item_redemption.delete()

    item_serializer = ItemSerializer(item_redemption.item)
    return Response({"message": "Item redemption used successfully", 
                     "item": item_serializer.data,
                     "customer_id": customer.id,
                     "updated_points": customer_points.num_points}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticatedAndActive])
def generate_ws_access_token(request):
    id = request.data.get("id")
    role = request.data.get("role")

    if not id or not role:
        return Response("Missing information.", status=400)
    
    payload = {"id": id, "role": role}

    # Set the token expiry to 15 minutes
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    # Add the expiry time to the payload
    payload["exp"] = int(expiry.timestamp())

    try:
        # Encode the JWT token using the SECRET_KEY_WS
        token = jwt.encode(payload, os.environ.get("SECRET_KEY_WS"), algorithm="HS256")

        return Response({"token": token.decode("utf-8")}, status=200)
    except Exception as e:
        return Response(str(e), status=500)
    
@api_view(['POST'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def add_friend(request):
    username = request.data.get("phone_number")

    if not username:
        return Response("Missing information.", status=400)

    try:
        friend = Customer.objects.get(username=username)
    except Customer.DoesNotExist:
        return Response("Customer not found", status=404)
    
    friendship = Friendship.objects.create(customer=request.user.customer, friend=friend)

    serializer = FriendshipSerializer(friendship)

    return Response(serializer.data, status=201)

@api_view(['POST'])
@permission_classes([CustomerPermissions, IsAuthenticatedAndActive])
def invite_friend(request):
    phone_number = request.data.get("phone_number")
    friend_name = request.data.get("name")
    first_name = request.user.customer.first_name
    last_name = request.user.customer.last_name

    if not phone_number:
        return Response("Missing information.", status=400)

    try:
        twilio_client.messages.create(
            body=f"Hey {friend_name}! \n\n" +
            f"{first_name} {last_name} invites you to PunchMe! The #1 social loyalty points program for free food, boba, and more! \n" +
            f"Download the app here and get your punches :) https://tools.applemediaservices.com/app/6447275121?country=us",
            from_=twilio_phone_number,
            to=str(phone_number),
        )
    except TwilioException as e:
        return Response({'error': 'Failed to send message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    return Response("message sent", status=200)