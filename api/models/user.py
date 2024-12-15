from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    """ 
    Object Manager for User model.
    
    Supports the following operations:

        1. Creating users
        2. Email validation
    """

    use_in_migrations = True

    def create_user(self, first_name, last_name, email, password=None, **kwargs: Any) -> Any:

        """Creates a new user model with email validation."""

        # Email validation
        if not email:
            raise ValueError(_('Email is required, please enter your email'))
        
        user = self.model(email=self.normalize_email(email).lower(), first_name=first_name, last_name=last_name, **kwargs)

        # Set password for user
        user.set_password(password)

        # Save the user to the database
        user.save(using=self._db)

        return user

    
    def create_superuser(self, first_name, last_name, email, password):

        """Creates a new admin user."""

        user = self.create_user(first_name=first_name, last_name=last_name, email=email, password=password)


        # Mark the admin users as superusers
        user.is_superuser = True

        user.save(using=self._db)

        return user
    


class User(AbstractBaseUser, PermissionsMixin):

    """Base User model."""

    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']
    