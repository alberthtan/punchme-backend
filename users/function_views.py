
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.response import Response

from users.views import CustomerSerializer

@api_view(['GET'])
@csrf_exempt
@login_required
@user_passes_test(lambda user: user.is_active)
def get_customer(request):
    user_serializer = CustomerSerializer(request.user)
    return Response(user_serializer.data)