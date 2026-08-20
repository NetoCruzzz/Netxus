from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.decorators import login_required

import requests
import tmdbsimple as tmdb

from .models import Discussion, Post
from .forms import PostForm


# TMDB API key
# Ernesto: Everything online says NOT to share your API key so create ".env" file in "netxus/App"
#          Create an account in tmdb website, you should get it for free as long as is for personal user, which it is in this case
#          and put 'TMDB_API_KEY= ....' put you API key after '=' then it should work, make sure you don't push your .env with you API key
tmdb.API_KEY = settings.TMDB_API_KEY


# Home page
def home(request):
    movies = Discussion.objects.all()
    trending = Discussion.objects.order_by('-postCount')[:5]
    newest = Discussion.objects.order_by('-created_at')[:5]

    return render(request, 'home.html', {
        'movies': movies,
        'trending': trending,
        'newest': newest
    })


# Search for movies using TMDB
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
            results = response.json().get("results", [])

    return render(request, "search_movies.html", {
        "query": query,
        "results": results
    })


#Neto: Add a movie from TMDB to the database
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

    if title:
        poster = data.get("poster_path")
        backdrop = data.get("backdrop_path")

        poster_url = ""
        banner_url = ""

        if poster:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster}"

        if backdrop:
            banner_url = f"https://image.tmdb.org/t/p/w1280{backdrop}"

        # Ernesto: Adds the movie to the database and avoids duplicates by using the movies' ID instead of title
        Discussion.objects.get_or_create(
            id=str(tmdb_id),                                                                # Ernesto: This line of code will make or break the posters/banners
            defaults={
                "name": title,
                "description": data.get("overview", ""),
                "pRating": data.get("vote_average", ""),
                "poster": poster_url,                                                       # Ernesto: Saves the TMDB poster link instead of downloading the image
                "banner": banner_url                                                        # Ernesto: Saves the TMDB banner link instead of downloading image
            }
        )

    return redirect('discussion', id=tmdb_id)

#Ulyses: Add a show from TMDB to the database
def add_show(request, tmdb_id):

    show = tmdb.TV(tmdb_id)
    show_info = show.info()
    name = show_info.get("name")
    descripton = show_info.get("overview", "")
    poster_path = show_info.get("poster_path")
    backdrop_path = show_info.get("backdrop_path") 
    rating = show_info.get("vote_average", "")

    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    banner_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else ""

    Discussion.objects.get_or_create(
        id=str(tmdb_id),
        defaults={
            "name": name,
            "description": descripton,
            "pRating": rating,
            "poster": poster_url,
            "banner": banner_url
        }
    )

    return redirect('discussion', id=tmdb_id)


# Register
# Ernesto: Handled the User Registration
def register_user(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = UserCreationForm()

    return render(request, 'register.html', {
        'form': form
    })


# Login
# Ernesto: Handled the User login 
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

                # Ernesto: ADDED so the user is sent back to the page they wanted before logging in
                next_page = request.GET.get('next')

                if next_page:
                    return redirect(next_page)

                return redirect('home')

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form
    })


# Profile
# Ernesto: Handled the user' profile
@login_required
def profile(request):
    return render(request, "profile.html")


# Edit profile
# Ernesto: ADDED so the user can edit their profile (Still needs some tweaks)
@login_required
def edit_profile(request):

    if request.method == 'POST':
        form = UserChangeForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'edit_profile.html', {
        'form': form
    })


# Logout
# Ernesto: Handled User Logout
def logout_user(request):
    logout(request)
    return redirect('home')                                                             # Ernesto: Sends user back to home page after logging out

# Shows a discussion and its posts
def discussion_page(request, id):
    movie = get_object_or_404(Discussion, id=id)
    posts = movie.posts.all().order_by("-created_at") #orders posts by newest first

    return render(request, "discussion.html", {
        "movie": movie,
        "posts": posts
    })

# Create a post
@login_required
def create_post(request, movie_id):

    movie = get_object_or_404(
        Discussion,
        id=movie_id
    )

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)

            post.movie = movie

            # Ernesto: ADDED so it saves the logged-in user as the author of the post
            post.user = request.user

            post.save()
            movie.postCount += 1
            movie.save()

            return redirect('discussion', id=movie.id)

    else:
        form = PostForm()

    return render(request, "create_post.html", {
        "form": form,
        "movie": movie
    })


# Edit a post
@login_required
def edit_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    # Ernesto: ADDED so only the person who made the post can edit it
    if post.user != request.user:
        return redirect('discussion', id=post.movie.id)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            instance=post
        )

        if form.is_valid():
            form.save()
            return redirect('discussion', id=post.movie.id)

    else:
        form = PostForm(instance=post)

    return render(request, "edit_post.html", {
        "form": form,
        "post": post
    })


# Delete a post
@login_required
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    # Ernesto: Only the person who made the post can delete it
    if post.user != request.user:
        return redirect('discussion', id=post.movie.id)

    if request.method == 'POST':
        movie_id = post.movie.id
        post.movie.postCount -= 1
        post.movie.save()
        post.delete()

        return redirect('discussion', id=movie_id)

    return render(request, "delete_post.html", {
        "post": post
    })


# Create a new discussion
def new_discussion(request):

    if request.method == "POST":

        movie_results = []
        show_results = []

        wanted = request.POST.get('searched_api', '')

        # Search for movies
        # Ernesto: UPDATED Searches TMDB for movies using the search bar (tmdb syntax)
        search = tmdb.Search()
        search.movie(query=wanted)

        for result in search.results:
            movie_results.append([
                result['title'],
                result['id'],
                result['poster_path'],
                result['overview'],
                result['release_date'],
                "movie",
            ])

        # Search for TV shows
        search.tv(query=wanted)

        for result in search.results:
            show_results.append([
                result['name'],
                result['id'],
                result['poster_path'],
                result['overview'],
                result['first_air_date'],
                "show",
            ])

        return render(request, "create_discussion.html", {
            "movie_results": movie_results,
            "show_results": show_results,
            "searched_api": wanted
        })

    return render(request, "create_discussion.html")


# Search discussions already in the database
def search_results(request):

    if request.method == "POST":

        searched = request.POST.get('searched', '')

        discussions = Discussion.objects.filter(
            name__contains=searched
        )

        return render(request, 'search_results.html', {
            'searched': searched,
            'discussions': discussions
        })
    else:
        discussions = Discussion.objects.all()
        return render(request, 'search_results.html', {
            'discussions': discussions
        })