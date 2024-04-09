from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.TextField(max_length= 500)
    creation_date = models.DateField(default=timezone.now().date())
    creation_time = models.TimeField(default=timezone.now().time())
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    def __str__(self):
        return f"""
                {self.content[:10]}
                ... posted by {self.user}. 
                Posted on {self.creation_date},
                {self.creation_time.strftime('%H:%M:%S')}
                """