# custom module for my forms
from .models import AuctionListing

from django import forms

class NewListingForm(forms.Form):
    title = forms.CharField(max_length="50", label="Title")
    description = forms.CharField(
        max_length="100", 
        widget=forms.Textarea
    )
    starting_bid = forms.IntegerField()
    image = forms.URLField(label="Add an image (URL)")
    type = forms.ChoiceField(choices= {
        "fashion": "Fashion", 
        "toys": "Toys", 
        "electronics": "Electronics",
        "home": "Home"
    })

class WatchlistForm(forms.Form):
    button_action = forms.CharField(widget=forms.HiddenInput, required=False)
    
class BidForm(forms.Form):
    bid = forms.IntegerField()

class DeleteForm(forms.Form):
    button_action = forms.CharField(widget=forms.HiddenInput, required=False)

class AddComment(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control mb-2',
                                                            'cols': 10,
                                                            'rows': 2,
                                                            'placeholder' : 'Your comment',
                                                            }), 
                                                max_length= 500)
    button_action = forms.CharField(widget=forms.HiddenInput, required=False)