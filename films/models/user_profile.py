from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null = False, related_name="profile")
    bio = models.TextField(null = True, blank = True)
    avatar = models.ImageField(null = True, blank = True)

    def __str__(self):
        return str(self.user.username)
