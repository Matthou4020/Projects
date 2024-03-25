from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, AuctionListing, Bid, Comment
from .forms import *

def index(request):
        active_listings = AuctionListing.objects.all()
        return render(request, "auctions/index.html", {
            "auctionlistings": active_listings
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new_listing(request):
    if request.method == "GET":
        return render(request, "auctions/new_listing.html", {
            "newlistingform": NewListingForm()
    })
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            imageurl = form.cleaned_data["image"]
            type = form.cleaned_data["type"]
            current_user = request.user            
            new_listing = AuctionListing(title=title, 
                                     description=description,
                                     startingbid=starting_bid,
                                     imageurl=imageurl,
                                     type=type,
                                     user=current_user
            )
            new_listing.save()
    else:
        form = NewListingForm()

    return HttpResponseRedirect(reverse("index"))

def listing(request, listing):
    current_listing = AuctionListing.objects.get(title=listing)
    watchlistform = WatchlistForm()
    if request.method == "GET":
        onwatchlist = current_listing.onwatchlist
        return render(request, "auctions/listing.html", {
            "listing": current_listing,
            "watchlistform": watchlistform,
            "onwatchlist": onwatchlist
        })
    
    if request.method == "POST":
        button_value = request.POST.get('button_value')
        if button_value == 'added':
            current_listing.onwatchlist = True
        
        elif button_value == 'deleted':
           current_listing.onwatchlist = False

        onwatchlist = current_listing.onwatchlist
        current_listing.save()
        return render(request, "auctions/listing.html", {
            "listing": current_listing,
            "watchlistform": watchlistform,
            "onwatchlist": onwatchlist
        })



@login_required
def watchlist(request):
    if request.method == "GET":
        current_user = request.user
        watchlist = AuctionListing.objects.filter(user=current_user, onwatchlist=True)
        watchlistform = WatchlistForm()
        return render (request, "auctions/watchlist.html",{
            "watchlist": watchlist,
            "watchlistform": watchlistform
        })
    if request.method == "POST":
        form = request.POST.get("button_value")
        title = form
        listing = AuctionListing.objects.get(title=title)
        listing.onwatchlist = False
        listing.save()
        return render(request, "auctions/watchlist.html")