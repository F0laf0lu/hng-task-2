from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from . managers import CustomUserManager

# Create your models here.

class User(AbstractUser):
    username = None
    userId = models.CharField(max_length=255, unique=True, editable=False)
    firstName = models.CharField(max_length=150, null=False)
    lastName = models.CharField(max_length=150, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstName", "lastName"]

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.userId:
            last_user = User.objects.order_by('id').last()
            if last_user:
                self.userId = f'{last_user.id + 1}'
            else:
                self.userId = 'user1'
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
    

class Organisation(models.Model):
    orgId = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='organisations')

    def __str__(self):
        return self.name