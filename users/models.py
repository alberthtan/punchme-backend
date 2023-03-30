import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone

from uuid import uuid4

def random_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", 'Customer'
        MANAGER = "MANAGER", 'Manager'

    role = models.CharField(max_length=50, choices=Role.choices, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.role:
            self.role = self.get_base_role()
        return super().save(*args, **kwargs)
        
    def get_base_role(self):
        return self.__class__.Role.CUSTOMER if issubclass(self.__class__, Customer) else self.__class__.Role.MANAGER

class Customer(User): 
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    USERNAME_FIELD = 'phone_number'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = self.get_base_role()

    def save(self, *args, **kwargs):
        self.username = self.phone_number
        super().save(*args, **kwargs)

class Manager(User):
    manager_email = models.EmailField(_('manager email address'), unique=True)
    USERNAME_FIELD = 'manager_email'

    def save(self, *args, **kwargs):
        self.username = self.manager_email
        super().save(*args, **kwargs)

class Restaurant(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    manager = models.OneToOneField(Manager, on_delete=models.CASCADE, related_name='restaurant')

    def __str__(self):
        return self.name
    
class Item(models.Model):
    name = models.CharField(max_length=255, blank=True)
    num_points = models.IntegerField(null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    
class CustomerPoints(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    num_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.customer.username} at {self.restaurant.name} ({self.num_points} points)"
    
class ItemRedemption(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid4, editable=False)
    
class EmailAuthentication(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6, default=random_code)
    is_verified = models.BooleanField(default=False)
    proxy_uuid = models.UUIDField(default=uuid4)

class PhoneAuthentication(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    code = models.CharField(max_length=6, default=random_code)
    is_verified = models.BooleanField(default=False)
    proxy_uuid = models.UUIDField(default=uuid4)