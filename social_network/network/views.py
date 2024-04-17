from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist


from .forms import PostForm
from .models import User, Post, Like


def index(request):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.user.is_authenticated:
        posts = Post.objects.order_by("-creation_date", "-creation_time") 
        paginator = Paginator(posts, 10)
        pages_total = paginator.count

        
        if request.GET.get('ajax') == 'True':
            data = json.loads(request.body)
            page_number = data.get("page_number")
            return JsonResponse({"message":"page number received"})
        
        if request.method == 'GET':
            user = request.user
            postform = PostForm()
            page_number = request.GET.get("page_number", 1)

            return render(request, "network/index.html",{
                "postform":postform,
                "recent_posts":paginator.page(page_number),
                "user":user,
                "paginator":paginator,
                "pages_total":pages_total,
            })
        
        if request.method == 'POST':
            form = PostForm(request.POST)
            user = request.user
            if form.is_valid():
                post_content = form.cleaned_data['content']
                post = Post(content=post_content,
                            user=user)
                post.save()
                return HttpResponseRedirect(reverse("index"))
            return render(request, "network/index.html", {
                'postform': form
            })
        
        return HttpResponseRedirect(reverse("index"))


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def profile(request, username):
    current_user = request.user
    profile = User.objects.get(username=username)
    posts = Post.objects.filter(user=profile).order_by("-creation_date")
    posts_count = posts.count()
    follows_count = profile.follows.count()
    followers_count = profile.follower.count()
    photo_url = profile.photo_url

    return render(request, "network/profile.html", {
        "username":username,
        "posts": posts,
        "profile":profile,
        "user":current_user,
        "followers_count": followers_count,
        "follows_count": follows_count,
        "posts_count": posts_count,
        "photo_url": photo_url
    })


@login_required
def following(request):
    current_user = request.user
    follows_list = current_user.follows.all()

    return render(request, "network/following.html", {
        "follows_list":follows_list,
    })


@csrf_exempt
@login_required
def user(request, username):
    current_user = request.user
    current_user = User.objects.get(username=current_user)

    if request.method == 'GET':
        user = User.objects.get(username=username)
        if user:
            follows = [user.username for user in current_user.follows.all()]
            data = {
                "follows" : follows
            }
            return JsonResponse(data)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get("action")
        
        if action == "follow":
            new_follows = data.get("follows")
            new_follows_id = User.objects.get(username=new_follows).id
            current_user.follows.add(new_follows_id)
            current_user.save()
            return JsonResponse({"message": "user succesfully added to the followed list"})
        
        elif action == "unfollow":
            follows = data.get("follows")
            follows_id = User.objects.get(username=follows).id
            current_user.follows.remove(follows_id)
            current_user.save()
            return JsonResponse({"message": "Succesfully deleted the user from the followed list"})
        


@login_required
@csrf_exempt
def posts(request):
    if request.method == "GET":
        likes = Like.objects.all()
        data = {
            likes:likes
        }


    if request.method == "PUT":
        data = json.loads(request.body)
        user_id = data.get("user_id")
        previous_content = data.get("previous_content")
        edited_content = data.get("edited_content")        
        previous_post = Post.objects.get(content=previous_content)
        
        if previous_content == edited_content:
            return HttpResponse(status=200)
        
        previous_post.content = edited_content
        previous_post.save()
        return HttpResponse(status=204)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get("user_id")
        post_id = data.get("post_id")
        action = data.get("action")

        if action == "like": 
            like = Like.objects.create(user_id=user_id, post_id=post_id)
            like.save()
            actualized_count = Like.objects.filter(post_id=post_id).count()
            return JsonResponse({"message":f"post succesfully liked",
                                 "actualizedCount":f"{actualized_count}"})
            
        if action =="unlike":
            like = Like.objects.get(post_id=post_id,user_id=user_id)
            like.delete()
            actualized_count = Like.objects.filter(post_id=post_id).count()
            return JsonResponse({"message":f"post succesfully unliked",
                                 "actualizedCount":f"{actualized_count}"})
        
        like_count = Like.objects.filter(post_id=post_id).count()

        try:
            Like.objects.get(user_id=user_id, post_id=post_id)
            has_liked = True
        except ObjectDoesNotExist:
            has_liked = False
        
        print(has_liked)
        return JsonResponse ({
            'hasLiked':has_liked,
            'likeCount':like_count
        })

