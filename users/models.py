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

    base_role = Role.CUSTOMER
    role = models.CharField(max_length=50, choices=Role.choices, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)
        
class Customer(User): 
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    USERNAME_FIELD = 'phone_number'

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
    item1 = models.CharField(max_length=255, blank=True)
    item1_points = models.IntegerField(null=True)
    item2 = models.CharField(max_length=255, blank=True)
    item2_points = models.IntegerField(null=True)
    item3 = models.CharField(max_length=255, blank=True)
    item3_points = models.IntegerField(null=True)
    manager = models.OneToOneField(Manager, on_delete=models.CASCADE, related_name='restaurant')

    def __str__(self):
        return self.name
    
class CustomerPoints(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    num_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.customer.username} at {self.restaurant.name} ({self.num_points} points)"
    
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