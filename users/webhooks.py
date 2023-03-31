from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from users.function_views import generate_qr
from users.models import Customer

@api_view(['PATCH'])
@csrf_exempt
def generate_qr_webhook(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return Response("Invalid Credentials", status=403)
    
    try:
        customer = Customer.objects.get(username=request.user.username)
    except Customer.DoesNotExist:
        return Response("customer does not exist", status=404)
    
    manager = request.data.get('code')

    # get manager and call

    # Call the generate_qr function with the HttpRequest object
    response = generate_qr(request._request)

    # Return a response to confirm that the webhook was received and processed correctly
    return Response("Webhook received and processed.", status=200)

