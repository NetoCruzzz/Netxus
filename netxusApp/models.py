from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#Model for Movies
class Discussion(models.Model):
    name = models.CharField(max_length=100)
    id = models.SlugField(unique=True, primary_key=True)
    description = models.TextField()
    pRating = models.CharField(max_length=10)
    
    poster = models.URLField(blank=True)
    banner = models.URLField(blank=True)
    
    postCount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    # Ernesto: String representation so movies names show up clearly in the admin/shell
    def __str__(self):
        return self.name

#Model for Posts
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    # Ernesto: Foreign key linking post to movies; if movie ideleted, delte its posts too
    #          related_name="posts" allows querying movie.posts.all() in views/templates
    movie = models.ForeignKey(
        Discussion,
        on_delete= models.CASCADE,
        related_name= "posts"
    )

    # Ernesto: Added Foreign key linking post to author; CASCADE deletes posts if user acc is removed
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Automatically records creation timestamp on initial save
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatically updates timestamp whenever the post is edited
    updated_at = models.DateTimeField(auto_now=True)

    # Ernesto: Display POST title in Django admin
    def __str__(self):
        return self.title