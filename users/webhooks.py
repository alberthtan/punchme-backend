from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from users.function_views import generate_qr
from users.models import Customer

@api_view(['POST'])
@csrf_exempt
def generate_qr_webhook(request):

    # Call the generate_qr function with the HttpRequest object
    response = generate_qr(request._request)

    # Return a response to confirm that the webhook was received and processed correctly
    return Response("Webhook received and processed.", status=200)

