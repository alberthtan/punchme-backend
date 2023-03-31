from users.function_views import generate_qr
from rest_framework.response import Response

def generate_qr_webhook(request):
    if request.method == 'POST':
        # Call the generate_qr view function
        generate_qr(request)
        return Response(status=200)
    else:
        return Response(status=405)