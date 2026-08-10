from django.db import models

# Create your models here.

#Model for Movies
class Movies(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    release_date = models.IntegerField()


    def __str__(self):
        return self.name

#Model for Posts
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    movie = models.ForeignKey(
        Movies, 
        on_delete= models.CASCADE,
        related_name= "posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title