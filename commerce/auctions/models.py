from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser): 
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True, default=None)
    description = models.CharField(max_length=100)
    startingbid = models.IntegerField()
    imageurl = models.URLField()
    type = models.CharField(max_length=20)
    onwatchlist = models.BooleanField(default=False)
    # Date of issue
    # End date

    def __str__(self): 
        return f"{self.title}, owned by {self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()#min and max
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids" )

    class Meta:
        db_table = 'auctions_bid'
        
    def __str__(self): 
        return f"bid of {self.amount} by {self.user} on {self.listing.title}"

class Comment(models.Model):
    text = models.TextField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comment")

    def __str__(self): 
        return f"{self.text} by {self.user} on {self.listing.title}"

