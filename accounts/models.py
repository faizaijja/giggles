# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Set default values for required fields if not provided
        if 'full_name' not in extra_fields:
            extra_fields['full_name'] = 'Admin User'
        if 'user_type' not in extra_fields:
            extra_fields['user_type'] = 'parent'

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom User model where email is used instead of username
    """
    USER_TYPE_CHOICES = [
        ('parent', 'Parent'),
        ('learner', 'Learner'),
    ]
    
    # Remove username field (we'll use email instead)
    username = None
    
    # Fields from your signup form
    email = models.EmailField(
        unique=True, 
        validators=[EmailValidator()],
        help_text='Required. Enter a valid email address.'
    )
    full_name = models.CharField(
        max_length=150, 
        help_text='Enter your full name'
    )
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='parent',
        help_text='Select whether you are a parent or learner'
    )
    
    # Additional fields
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Use our custom manager
    objects = CustomUserManager()
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'user_type']
    
    class Meta:
        db_table = 'giggles_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return "{} ({})".format(self.full_name, self.email)

    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email
    
    
    

