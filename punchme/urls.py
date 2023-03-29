"""punchme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import CustomerViewSet, ManagerViewSet, RestaurantViewSet, CustomerPointsViewSet
from users.login_views import SendPhoneCode, RegisterVerifyPhoneCode, LoginVerifyPhoneCode
from users.login_views import SendEmailCode, RegisterVerifyEmailCode, LoginVerifyEmailCode
from users.function_views import get_customer, update_customer
from users.function_views import get_manager


from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'customer-points', CustomerPointsViewSet, basename='customerpoints')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('send-phone-code/', SendPhoneCode.as_view()),
    path('register-verify-phone-code/', RegisterVerifyPhoneCode.as_view()),
    path('login-verify-phone-code/', LoginVerifyPhoneCode.as_view()),
    path('send-email-code/', SendEmailCode.as_view()),
    path('register-verify-email-code/', RegisterVerifyEmailCode.as_view()),
    path('login-verify-email-code/', LoginVerifyEmailCode.as_view()),

    path('get-customer', get_customer),
    path('update-customer/', update_customer),

    path('get-manager', get_manager),
]

urlpatterns += router.urls