from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    AuctionName = models.CharField(max_length=50)
    HighestBidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="highestbidder")

class Bids(models.Model):
    BidAmount = models.IntegerField(max_length = 9)

class Comments(models.Model):
    Comment = models.TextField(max_length=200)