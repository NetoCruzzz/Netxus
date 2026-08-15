from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views #for account management

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('create/', views.create_post, name='create_post'),
    #path(
      #  'movies/<int:movie_id>/',
     #   views.movies,
     #   name='movies'),
    path("create/", views.create_post, name="create_post"),
    path("discussion/<slug:id>/", views.discussion_page, name="discussion"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)