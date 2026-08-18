from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

import requests

from .models import Movies, Post    # Ernesto: Added Post import to avoid NameError in edit_post
from .forms import PostForm


# Home View
# Ernesto: Added TMDB API to fetch poster images
def home(request):
    movies = Movies.objects.all()

    # Ernesto: Loop through each movie in our DB to fetch matching poster path from TMDB
    for movie in movies:
        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": settings.TMDB_API_KEY,
            "query": movie.name
        }

        response = requests.get(url, params=params)

        # Ernesto: Check if TMDB request succeeded and got results
        if response.status_code == 200:
            data = response.json()

            # Ernesto: Grab the first search result's poster path if available
            if data["results"]:
                movie.poster_path = data["results"][0]["poster_path"]
                print(movie.name, movie.poster_path)
            else:
                movie.poster_path = None
        else:
            movie.poster_path = None

    return render(
        request,
        'home.html',
        {
            'movies' : movies
        }
    )

# Register Info
# Handles user sign-ups via Django's built-in UserCreationForm
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect ('home')

    else:
        # GET request: send an empty form to display
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# Login Info
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Credentials check against DB
            user = authenticate(
                username=username, 
                password=password
                )
            
            if user is not None:
                login(request, user)
                
                # Ernesto: If redirected here by @login_required, send them back to where they were going
                #         Example - If someone is logged in and tries to create a post then they will be sent to login page, after logging in they will be back to their original post
                next_page = request.GET.get('next')

                if next_page:
                    return redirect(next_page)

                return redirect('home')

    else:
        form = AuthenticationForm()

    return render(request, "login.html", {'form': form})

# Ernesto: Profile protection so other users only access their own profile
@login_required
def profile(request):
    return render(request, "profile.html")

# Ernesto: Added user's to edit their profile
@login_required
def edit_profile(request):

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile')
    
    else:
        form = UserChangeForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})

# Logout
def logout_user(request):
    logout(request)
    return redirect('home')

# Movie details
def movies(request, movie_id):
    # Gets movie by ID or 404 if not found
    movie = get_object_or_404(
        Movies, 
        id=movie_id
    )
    posts = movie.posts.all().order_by("-created_at")

    return render(
        request,
        "movies.html",
        {
            "movie": movie,
            "posts": posts
        }

    )

# Create Post
@login_required
def create_post(request, movie_id):

    movie = get_object_or_404(Movies, id=movie_id)

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            # Ernesto: Holding off on saving to DB so we can assign Foreign Keys first
            post = form.save(commit=False)
            post.movie = movie
            post.user = request.user
            post.save()

            return redirect('movies', movie_id=movie.id)

    else:
        form = PostForm()

    return render(
        request,
        "create_post.html",
        {
            "form": form,
            "movie": movie
        }
    )

# Ernesto: Added Edit Post
@login_required
def edit_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    # Ernesto: Permission Check to Edit Posts
    # post.user != request.user will basically be like post.user == request.user then they can edit, but if someone else owns it then they can't edit it
    if post.user != request.user:
        return redirect('movies', movie_id=post.movie.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            form.save()
            return redirect('movies', movie_id=post.movie.id)
    else:
        form = PostForm(instance=post)
    
    return render(
        request,
        "edit_post.html",
        {
            "form": form,
            "post": post
        }
    )

@login_required
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)                  # Ernesto: Supposed to find the post to delete

    if post.user != request.user:
        return redirect('movies', movie_id=post.movie.id)       # Ernesto: Supposed to prevent someone else delete a post that's not theirs
    
    if request.method == 'POST':                                
        movie_id = post.movie.id
        post.delete()                                           # Ernesto: Only delete post when user submits a POST request

        return redirect('movies', movie_id=movie_id)
    
    return render(
        request,
        "delete_post.html",
        {
            "post": post
        }
    )