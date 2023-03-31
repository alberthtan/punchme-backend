from users.function_views import generate_qr
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_qr_webhook(request):
    if request.method == 'POST':
        # Call the generate_qr view function
        generate_qr(request)
        response = Response(status=200)
        response.accepted_renderer = None  # Set accepted_renderer to None
        return response
    else:
        return Response(status=405)
