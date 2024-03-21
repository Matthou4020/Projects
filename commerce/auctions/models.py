from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True, default=None)
    startingbid = models.IntegerField()
    imageurl = models.URLField()
    type = models.CharField(max_length=20)




class Bids(models.Model):
    BidAmount = models.IntegerField()

class Comments(models.Model):
    Comment = models.TextField(max_length=200)