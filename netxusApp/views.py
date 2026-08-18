from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

import requests

from .models import Movies
from .forms import PostForm


#home view
def home(request):
    movies = Movies.objects.all()

    for movie in movies:
        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": settings.TMDB_API_KEY,
            "query": movie.name
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

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
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect ('home')

    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# Login Info
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                username=username, 
                password=password
                )
            
            if user is not None:
                login(request, user)
                return redirect('home')

    else:
        form = AuthenticationForm()

    return render(request, "login.html", {'form': form})

@login_required
def profile(request):
    return render(request, "profile.html")

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

def movies(request, movie_id):
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
def create_post(request, movie_id):

    movie = get_object_or_404(Movies, id=movie_id)

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
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