from django.db import models
from django.contrib.auth.models import User

class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=63)
    email = models.CharField(max_length=63)
    password = models.CharField(max_length=63)
    repeated_password = models.CharField(max_length=63)
    
    def __str__(self):
        return self.user.username