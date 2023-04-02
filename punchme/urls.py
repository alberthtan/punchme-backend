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
from users.views import CustomerViewSet, ManagerViewSet, RestaurantViewSet, ItemViewSet, CustomerPointsViewSet
from users.views import ItemRedemptionViewSet, RestaurantQRViewSet
from users.login_views import SendPhoneCode, RegisterVerifyPhoneCode, LoginVerifyPhoneCode
from users.login_views import SendEmailCode, RegisterVerifyEmailCode, LoginVerifyEmailCode
from users.function_views import get_customer, update_customer, delete_customer, create_redemption, delete_redemption, award_point
from users.function_views import get_manager, update_manager, delete_manager, create_item, update_item
from users.function_views import delete_item, generate_qr, get_qr, validate_redemption, generate_ws_access_token
from users.get_function_views import get_customer_points, get_customer_points_list, get_customer_points_manager_view
from users.get_function_views import get_items_by_restaurant, get_restaurant, get_customer_points_manager_view

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'customer-points', CustomerPointsViewSet, basename='customerpoints')
router.register(r'item-redemption', ItemRedemptionViewSet, basename='itemredemption')
router.register(r'restaurant-qr', RestaurantQRViewSet, basename='restaurantqr')

urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('admin/', admin.site.urls),
    path('send-phone-code/', SendPhoneCode.as_view()),
    path('register-verify-phone-code/', RegisterVerifyPhoneCode.as_view()),
    path('login-verify-phone-code/', LoginVerifyPhoneCode.as_view()),
    path('send-email-code/', SendEmailCode.as_view()),
    path('register-verify-email-code/', RegisterVerifyEmailCode.as_view()),
    path('login-verify-email-code/', LoginVerifyEmailCode.as_view()),

    path('get-customer', get_customer),
    path('update-customer/', update_customer),
    path('delete-customer/', delete_customer),
    path('create-redemption/', create_redemption),
    path('delete-redemption/<int:redemption_id>/', delete_redemption),
    path('award-point/', award_point),

    path('get-manager', get_manager),
    path('update-manager/', update_manager),
    path('delete-manager/', delete_manager),
    path('create-item/', create_item),
    path('update-item/', update_item),
    path('delete-item/<int:item_id>/', delete_item),
    path('generate-qr/', generate_qr, name='generate-qr'),
    path('get-qr', get_qr),
    path('validate-redemption/', validate_redemption), 

    path('get-restaurant/<int:restaurant_id>', get_restaurant), 
    path('get-customer-points-by-restaurant/<int:restaurant_id>', get_customer_points),
    path('get-customer-points-list', get_customer_points_list), 
    path('get-customer-points-manager-view', get_customer_points_manager_view),
    path('get-items-by-restaurant/<int:restaurant_id>', get_items_by_restaurant),
    path('get-customer-manager-view/<int:customer_id>', get_customer_manager_view), 

    path('generate-ws-access-token/', generate_ws_access_token),

]

urlpatterns += router.urls