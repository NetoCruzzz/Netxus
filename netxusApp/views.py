from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import requests
import tmdbsimple as tmdb

from .models import Discussion, Post    # Ernesto: Added Post import to avoid NameError in edit_post
from .forms import PostForm
from . import models
from . import forms

#loading API key for TMDB API
tmdb.API_KEY = settings.TMDB_API_KEY

# Home View
# Ernesto: Added TMDB API to fetch poster images
def home(request):
    trending = models.Discussion.objects.order_by('-postCount')[:5]  # Get the top 5 discussions based on postCount
    newest = models.Discussion.objects.order_by('-created_at')[:5]  # Get the 5 most recently created discussions

    return render(
        request,
        'home.html',
        {
            'trending': trending,
            'newest': newest
        }
    )


# Search TMDB for movies
def search_movies(request):

    query = request.GET.get('query', '').strip()

    results = []

    if query:
        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": settings.TMDB_API_KEY,
            "query": query
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            for movie in data.get("results", []):
                results.append(movie)

    return render(
        request,
        "search_movies.html",
        {
            "query": query,
            "results": results
        }
    )


def add_movie(request, tmdb_id):

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

    params = {
        "api_key": settings.TMDB_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return redirect('home')

    data = response.json()

    title = data.get("title")
    overview = data.get("overview")
    release_date = data.get("release_date", "")

    if release_date:
        release_year = int(release_date[:4])
    else:
        release_year = 0

    # Ulyses: Discussion replaced the old Movies model.
    # Ernesto: Keeping the TMDB movie search/add functionality while using the new Discussion model.
    if title:
        discussion_id = title.lower().replace(" ", "-")

        Discussion.objects.get_or_create(
            id=discussion_id,
            defaults={
                "name": title,
                "description": overview or "",
                "pRating": data.get("vote_average", "")
            }
        )

    return redirect('home')


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
        Discussion,
        id=movie_id
    )
    posts = movie.posts.all().order_by("-created_at")

    return render(
        request,
        "discussion.html",
        {
            "movie": movie,
            "posts": posts
        }

    )


# Create Post
@login_required
def create_post(request, movie_id):

    movie = get_object_or_404(Discussion, id=movie_id)

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


#shows information about a specific discussion and its posts
def discussion_page(request, id):
    movie = models.Discussion.objects.get(id=id)
    posts = movie.posts.all().order_by("-created_at")

    return render(
        request,
        "discussion.html",
        {
            "movie": movie,
            "posts": posts
        }
    )


#creating a new discussion
def new_discussion(request):
    #if movie/show is searched for:
    #create a search query to TMDB API
    #
    if request.method == "POST":
        movie_results=[]
        show_results=[]
        wanted = request.POST['searched_api']
        search = tmdb.Search()
        search.movie(query=wanted)
        for result in search.results:
            movie_results.append([result['title'], result['id']])
        search.tv(query=wanted)
        for result in search.results:
            show_results.append([result['name'], result['id']])
        return render(request, "create_discussion.html", {"movie_results": movie_results, "show_results": show_results})
    else:
        return render(request, "create_discussion.html", {})


#search results view
def search_results(request):
    if request.method == "POST":
        searched = request.POST['searched']
        discussions = models.Discussion.objects.filter(name__contains=searched)
        return render(request, 'search_results.html',
        {'searched': searched, 'discussions': discussions})
    else:
        return render(request, 'search_results.html',
        {})