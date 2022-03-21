from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
# AbstractBaseUser is the default user model in Django and it is used to create the user model in the database.
# BaseUserManager is the default manager for the user model in Django and used to create users and groups in the database.
# permissions.py is the default permission model in Django and used to create permissions for the user model in the database.
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken # refresh token is used to generate a new token for the user


class UserManager(BaseUserManager): # create a class for the user manager

    def create_user(self, f_name, l_name, email, password=None, confirmpassword=None): # create a user method

        if f_name is None:
            raise TypeError("User Should have name")
        if l_name is None:
            raise TypeError("User Should have name")
        '''if username is None:
            raise TypeError('Users should have a username')'''
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(email=self.normalize_email(email), f_name=f_name, l_name=l_name) 
        # creating a user object with the email and password fields filled in the database 
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None): # create a superuser method for the user manager 
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


'''AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}'''


class User(AbstractBaseUser, PermissionsMixin): # create permission model for the user
    f_name = models.CharField(max_length=255, null=False)
    l_name = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True)
    # username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255, null=False)
    # confirmpassword = models.CharField(max_length=255)
    # company = models.CharField(max_length=255)
    '''city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)'''
    mobileno = models.IntegerField(null=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class Organization(models.Model): # create a table for the organization
    # company_id = models.ForeignKey(User, related_name='organization', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, null=False)


class app_role(models.Model): # create a table for the app_role
    role_name = models.CharField(max_length=255, null=False)
    role_mapping = models.CharField(max_length=255)


class Address(models.Model): # create a table for the address 
    # add_id = models.ForeignKey(User, related_name='add_id', on_delete=models.CASCADE)
    city = models.CharField(max_length=255, null=False)
    state = models.CharField(max_length=255, null=False)
    country = models.CharField(max_length=255, null=False)


class bussiness_domain(models.Model): # create a table for the bussiness_domain
    domain_name = models.CharField(max_length=255, null=False)
