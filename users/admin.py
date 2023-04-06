from django.contrib import admin

from users.models import Customer, Manager, Restaurant, Item, CustomerPoints, ItemRedemption, RestaurantQR
from users.models import PhoneAuthentication, EmailAuthentication, Friendship

# Register your models here.

admin.site.register(Customer)
admin.site.register(Manager)
admin.site.register(Restaurant)
admin.site.register(Item)
admin.site.register(CustomerPoints)
admin.site.register(ItemRedemption)
admin.site.register(RestaurantQR)
admin.site.register(PhoneAuthentication)
admin.site.register(EmailAuthentication)
admin.site.register(Friendship)
