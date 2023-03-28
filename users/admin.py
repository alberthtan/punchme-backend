from django.contrib import admin

from users.models import Customer, Manager, Restaurant

# Register your models here.

admin.site.register(Customer)
admin.site.register(Manager)
admin.site.register(Restaurant)
