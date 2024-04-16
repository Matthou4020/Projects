
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    
    # API routes
    path("posts", views.posts, name="posts"),
    path("users/<str:username>", views.user, name="user"),

    path("<str:username>", views.profile, name="profile")
]
