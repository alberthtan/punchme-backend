import random
import django.dispatch

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage

from uuid import uuid4

restaurant_signal = django.dispatch.Signal()

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
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # check if the customer object already exists in the database
        try:
            # retrieve the existing object from the database
            existing_obj = Customer.objects.get(pk=self.pk)
        except Customer.DoesNotExist:
            # the object does not exist yet, so there's nothing to delete
            pass
        else:
            # if the profile picture has changed, delete the old file from S3
            if existing_obj.profile_picture and existing_obj.profile_picture != self.profile_picture:
                default_storage.delete(existing_obj.profile_picture.name)
        self.username = self.phone_number
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete the profile picture file from S3 when the object is deleted
        if self.profile_picture:
            default_storage.delete(self.profile_picture.name)
        super().delete(*args, **kwargs)

class Friendship(models.Model):
    customer = models.ForeignKey(Customer, related_name='friendship_creator_set', on_delete=models.CASCADE)
    friend = models.ForeignKey(Customer, related_name='friend_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'friend')

class PushToken(models.Model):
    customer = models.ForeignKey(Customer, related_name='push_notifications', on_delete=models.CASCADE)
    token = models.CharField(max_length=255)

class Manager(User):
    manager_email = models.EmailField(_('manager email address'), unique=True)
    employee_code = models.PositiveIntegerField(_('employee code'), default=0)
    USERNAME_FIELD = 'manager_email'

    def save(self, *args, **kwargs):
        self.username = self.manager_email
        super().save(*args, **kwargs)

class Restaurant(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    manager = models.OneToOneField(Manager, on_delete=models.CASCADE, related_name='restaurant')
    restaurant_image = models.FileField(upload_to='restaurants/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            existing_obj = Restaurant.objects.get(pk=self.pk)
        except Restaurant.DoesNotExist:
            pass
        else:
            if existing_obj.restaurant_image and existing_obj.restaurant_image != self.restaurant_image:
                default_storage.delete(existing_obj.restaurant_image.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete the profile picture file from S3 when the object is deleted
        if self.restaurant_image:
            default_storage.delete(self.restaurant_image.name)
        super().delete(*args, **kwargs)

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
    timestamp = models.DateTimeField(default=timezone.now)
    give_point_eligible = models.BooleanField(default=False)  # to track if a customer has earned a point for friends feature

    def __str__(self):
        return f"{self.customer.username} at {self.restaurant.name} ({self.num_points} points)"
    
class ItemRedemption(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid4, editable=False)

class Referral(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    phone_number = models.CharField(validators=[phone_regex], max_length=17)

class RestaurantQR(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid4)

class Transaction(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    customer_string = models.TextField()
    transaction_date = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=6) # point or reward
    transaction_reward = models.CharField(max_length=255, null=True, blank=True) # item in transaction if reward
    num_points = models.IntegerField() # number of points involved in the transaction
    
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