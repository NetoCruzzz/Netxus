from django.db import models

# Create your models here.

#Model for Movies
class Discussion(models.Model):
    name = models.CharField(max_length=100)
    id = models.SlugField(unique=True, primary_key=True)
    description = models.TextField()
    pRating = models.CharField(max_length=10)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    postCount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

#Model for Posts
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    movie = models.ForeignKey(
        Discussion, 
        on_delete= models.CASCADE,
        related_name= "posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title