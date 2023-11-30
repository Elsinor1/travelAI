from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json


from .forms import NewPostForm
from .models import User, Post, Like, Follow


def index(request):
    # Handle new post request
    if request.method == "POST":
        is_added: bool = add_new_post(request)
        if is_added:
            HttpResponseRedirect(reverse("index"))
        else:
            new_post_form = NewPostForm(request.POST)

    # Get the posts ordered by date in descending order
    all_posts = Post.objects.all().order_by("-date")
    # Set the pagination
    paginator = Paginator(all_posts, 10) # Show 10 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Check if new_post_form has been already defined, if not, define it
    try:
        if new_post_form:
            pass
    except UnboundLocalError:
        new_post_form = NewPostForm()

    liked_post_query = Post.objects.filter(likes__author=request.user.id)

    # Render index page
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "new_post_form": new_post_form,
        "liked_post_query": liked_post_query
    })

@login_required
def add_new_post(request) -> bool:
        new_post = NewPostForm(request.POST)
        if new_post.is_valid():
            post = Post(
                author=request.user,
                text=new_post.cleaned_data["text"],
                date=datetime.now()
                )
            post.save()
            return True
        else:
            return False


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

def display_user(request, user_id):
    displayed_user = User.objects.get(id=user_id)
    posts_by_user = Post.objects.filter(author=displayed_user).order_by("-date")

    # Pagination
    paginator = Paginator(posts_by_user, 8) # Show 10 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Query for setting up like buttons
    liked_post_query = Post.objects.filter(likes__author=request.user.id)

    return render(request, "network/display_user.html", {
        "displayed_user":displayed_user,
        "page_obj": page_obj,
        "liked_post_query": liked_post_query,
    })

@login_required
def following(request):
    # Get the posts of followed users ordered by date in descending order
    user = User.objects.get(pk=request.user.id)
    followed_by_active_user = User.objects.filter(followed_by__follower=user)
    posts_by_followed_by_active_user = Post.objects.filter(author__in=followed_by_active_user).order_by("-date")
    # Set the pagination
    paginator = Paginator(posts_by_followed_by_active_user, 10) # Show 10 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Query for setting up like buttons
    liked_post_query = Post.objects.filter(likes__author=request.user.id)

    # Render index page
    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "liked_post_query": liked_post_query,
    })

# API for follow
@login_required
@csrf_exempt
def follow_user(request, user_id):
    # Query for user data
    # Users followed by active user
    followed_by_active_user: QuerySet = User.objects.filter(followed_by__follower=request.user)
    followed_by_active_user_count = followed_by_active_user.count()
    # Displayed user
    followed_user: User = User.objects.get(id=user_id)
    # Users followed by displayed user
    followed_by_displayed_user: QuerySet = followed_user.following

    if request.method == "PUT":
        # If followed, remove from follow
        if followed_user in followed_by_active_user:
            # Remove follow
            follow = Follow.objects.get(follower=request.user, followed=followed_user)
            follow.delete()
            print(f"Follow of user {followed_user.username} has been deleted")
            followed = False
            followed_by_active_user_count -= 1
        # Else add to follow
        else:
            # Add follow
            Follow.objects.create(follower=request.user, followed=followed_user)
            print(f"Follow of user {followed_user.username} has been created")
            followed = True
            followed_by_active_user_count += 1

    elif request.method == "GET":
        if followed_user in followed_by_active_user:
            followed = True
        else:
            followed = False

    # Request must be PUT or GET
    else:
        print("GET or PUT request required.")
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

    # Return JsonResponse True if followed
    return JsonResponse({
        "is_followed": followed,
        "follows_count": followed_by_displayed_user.count(),
        "followed_by_count": followed_by_active_user_count,
    }, status=200)



@login_required
@csrf_exempt
def like_post(request, post_id):
    # Query for post data
    this_post = Post(id=post_id)
    liked_by_user: Like = Like.objects.filter(post=this_post, author=request.user)
    is_liked: bool = liked_by_user.count() > 0

    if request.method == "PUT":
        if is_liked:
            Like.objects.get(post=this_post, author=request.user).delete()
            is_liked = False
            print("User unliked the post")
        else:
            Like.objects.create(post=this_post, author=request.user)
            is_liked = True
            print("User liked the post")
    elif request.method == "GET":
        pass

    # Request must be PUT or GET
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

    # Return JsonResponse True if liked by user
    return JsonResponse({
        "is_liked": is_liked,
        "likes_count": this_post.likes.count(),
    }, status=200)


@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            text = data["post_text"]
            print(text)
            post = Post.objects.get(id=post_id)
            post.text = text
            post.save()
            return JsonResponse({"mesage": "Post updated successfully"}, status=200)
        except Post.DoesNotExist:
            print("not exists")
            return JsonResponse({"message": "Post does not exist"}, status=404)
        except Exception as e:
            print(e, "exception last")
            return JsonResponse({"message": str(e)}, status=500)
    return JsonResponse({"message": "Invalid request method"}, status=400)
