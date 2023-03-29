from django.contrib import admin

from users.models import Customer, Manager, Restaurant, CustomerPoints, PhoneAuthentication, EmailAuthentication

# Register your models here.

admin.site.register(Customer)
admin.site.register(Manager)
admin.site.register(Restaurant)
admin.site.register(CustomerPoints)
admin.site.register(PhoneAuthentication)
admin.site.register(EmailAuthentication)
