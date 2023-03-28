from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

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

class Manager(User):
    manager_email = models.EmailField(_('manager email address'), unique=True)
    USERNAME_FIELD = 'manager_email'


# class CustomerManager(BaseUserManager):
#     def create_user(self, phone_number, first_name, last_name, email=None, password=None):
#         if not phone_number:
#             raise ValueError('Phone number is required')
#         customer = self.model(
#             phone_number=phone_number,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#         )
#         customer.set_password(password)
#         customer.save(using=self._db)
#         return customer

#     def create_superuser(self, phone_number, first_name, last_name, email, password):
#         customer = self.create_user(
#             phone_number=phone_number,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             password=password,
#         )
#         customer.is_staff = True
#         customer.is_superuser = True
#         customer.save(using=self._db)
#         return customer

# class Customer(AbstractBaseUser, PermissionsMixin):
#     phone_regex = RegexValidator(
#         regex=r'^\+?1?\d{9,15}$',
#         message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
#     )
#     phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     email = models.EmailField(max_length=255, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = CustomerManager()

#     USERNAME_FIELD = 'phone_number'
#     EMAIL_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name']

#     def get_full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def get_short_name(self):
#         return self.first_name

#     def __str__(self):
#         return self.phone_number

# class ManagerManager(BaseUserManager):
#     def create_user(self, email, password, first_name, last_name):
#         if not email:
#             raise ValueError(_('The Email field must be set'))
#         user = self.model(
#             email=self.normalize_email(email),
#             first_name=first_name,
#             last_name=last_name,
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password, first_name, last_name):
#         user = self.create_user(
#             email=email,
#             password=password,
#             first_name=first_name,
#             last_name=last_name,
#         )
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user

# class Manager(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = ManagerManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name']

#     def get_full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def get_short_name(self):
#         return self.first_name

#     def __str__(self):
#         return self.email
