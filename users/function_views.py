
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import status
from rest_framework.response import Response

from users.models import Customer
from users.views import CustomerSerializer


@api_view(['GET'])
@csrf_exempt
def get_customer(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)
    
    user_serializer = CustomerSerializer(request.user)

    return Response(user_serializer.data)