from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    class Meta:
        db_table = "profile"