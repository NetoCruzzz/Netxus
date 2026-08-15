from django import forms
from .models import Post, Discussion

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'movie',
            'title',
            'content',
        ]

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = [
            'name',
            'id',
            'description',
            'pRating',
            'poster',
            'banner',
        ]