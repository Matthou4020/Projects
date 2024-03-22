# custom module for my forms

from django import forms

class NewListingForm(forms.Form):
    title = forms.CharField(max_length="50", label="Title")
    description = forms.CharField(
        max_length="100", 
        widget=forms.Textarea
    )
    
    starting_bid = forms.IntegerField()
    image = forms.URLField(label="Add an image")
    type = forms.ChoiceField(choices= {
        "fashion": "Fashion", 
        "toys": "Toys", 
        "electronics": "Electronics",
        "home": "Home"
    })