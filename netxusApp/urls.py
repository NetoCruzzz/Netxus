from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views #for account management

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path(
        'movies/<int:movie_id>/',
        views.movies,
        name='movies'),

    path('movies/<int:movie_id>/create/', 
    views.create_post, 
    name="create_post"),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile')
]