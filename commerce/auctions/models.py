from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class User(AbstractUser): 
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True, default=None)
    description = models.CharField(max_length=100)
    startingbid = models.IntegerField(default=0)
    imageurl = models.URLField()
    type = models.CharField(max_length=20)
    highestbid = models.IntegerField(default=0)
    won = models.BooleanField(default=False)
    # category = models.CharField()
    # Date of issue
    # End date

    def __str__(self): 
        return f"{self.title}, owned by {self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids" )

    def __str__(self): 
        return f"bid of {self.amount} by {self.user} on {self.listing.title}"

class Comment(models.Model):
    text = models.TextField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comment")

    def __str__(self): 
        return f"{self.text} by {self.user} on {self.listing.title}"
    
class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlists")

    def clean(self):
        if WatchList.objects.filter(user=self.user, listing=self.listing).exists():
            raise ValidationError('This listing is already in the user\'s watchlist.')

class AuctionWinner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winners")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="winners")