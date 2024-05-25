from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, AuctionListing, Bid, Comment, WatchList, AuctionWinner
from .forms import NewListingForm, WatchlistForm, BidForm, DeleteForm, AddComment
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

def index(request):
        active_listings = AuctionListing.objects.filter(won=False)
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
                                     user=current_user,
                                     highestbid=starting_bid
            )
            new_listing.save()
    
    else:
        form = NewListingForm()

    return HttpResponseRedirect(reverse("index"))


def listing(request, listing):
    current_listing = AuctionListing.objects.get(title=listing)
    watchlistform = WatchlistForm()
    bidform = BidForm()
    highestbid = current_listing.highestbid
    user = request.user
    watchlist = WatchList.objects.filter(listing=current_listing)
    listing_owner = AuctionListing.objects.get(title=listing).user
    addcomment = AddComment()

    try:
        comments = Comment.objects.filter(listing=current_listing)

    except ObjectDoesNotExist:
        pass

    try:
        winner = AuctionWinner.objects.get(listing=current_listing)
        if winner:
            if user == winner.user:
                return render(request, "auctions/winner.html", {
                    "listing":current_listing
                })
            else:
                return render(request, "auctions/listingover.html")
    except ObjectDoesNotExist:
        pass
    if listing_owner == user:
        owner = True
    else:
        owner = False
    if request.method == "GET":
        return render(request, "auctions/listing.html", {
            "listing": current_listing,
            "watchlistform": watchlistform,
            "bidform": bidform,
            "highestbid":highestbid,
            "watchlist": watchlist,
            "owner": owner,
            "comments":comments,
            "addcomment":addcomment
        })

    if request.method == "POST":
        form = DeleteForm(request.POST)
        button_action = request.POST.get("button_action")
        if button_action == "end_listing":
            current_listing.won = True
            current_listing.save()
            
            winningbid = get_object_or_404(Bid, amount=current_listing.highestbid)
            winner = winningbid.user

            AuctionWinner.objects.create(user=winner, listing=current_listing)
        
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["bid"]
            if amount <= current_listing.highestbid:
                raise ValueError("Bid amount must be greater than the starting bid.")
            user = request.user
            bid = Bid(user=user, amount=amount, listing=current_listing)
            bid.save()
            current_listing.highestbid = amount
            highestbid = amount
            current_listing.save()
            return HttpResponseRedirect(listing)

        form = WatchlistForm(request.POST)
        button_action = request.POST.get("button_action")
        if button_action == "add_watchlist":
            new_watchlist = WatchList.objects.create(listing=current_listing, user=user)
            new_watchlist.save()
        elif button_action == "remove_watchlist":
            WatchList.objects.get(listing=current_listing).delete()

        form = AddComment(request.POST)
        if form.is_valid():
            button_action = form.cleaned_data["button_action"]
            if button_action == "add_comment":
                text = form.cleaned_data["text"]         
                newcomment = Comment.objects.create(text=text, user=user, listing=current_listing)
                newcomment.save()
        
        return HttpResponseRedirect(listing)
    return HttpResponseRedirect(listing)

@login_required
def watchlist(request):
    current_user = request.user
    watchlist = WatchList.objects.filter(user=current_user)
    if request.method == "GET":
        watchlistform = WatchlistForm()
        return render (request, "auctions/watchlist.html",{
            "watchlist": watchlist,
            "watchlistform": watchlistform
        })
    
    if request.method == "POST":
        form = request.POST.get("button_value")
        if form:
            WatchList.objects.filter(id=form).delete()
            return HttpResponseRedirect("watchlist")
        else:
            return HttpResponseRedirect("")

def categories(request):
    auctionlistings = AuctionListing.objects.filter(won=False)
    categories = set()
    for listing in auctionlistings:
        categories.add(listing.type)

    return render (request, "auctions/categories.html", {
        "categories":categories,
    })
 
def category(request, category):
    listings = AuctionListing.objects.filter(type=category, won=False)
    return render(request, "auctions/category.html", {
        "listings":listings

    })