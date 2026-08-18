from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views #for account management

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Ernesto: Passes movie_id to load specific movie forum
    path(
        'movies/<int:movie_id>/',
        views.movies,
        name='movies'),

    # Ernesto: Captures movie_id so the new post attaches to the correct movie
    path('movies/<int:movie_id>/create/', 
    views.create_post, 
    name="create_post"),

    # Ernesto: Gets post_id to edit or delete a secific post
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    # Ernesto: Added delete post
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # Ernesto: Anything relating to User's profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search_movies, name='search_movies'),
    path('movies/add/<int:tmdb_id>/', views.add_movie, name='add_movie'),
]