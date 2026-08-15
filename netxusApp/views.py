from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . import models
from . import forms


#home view
def home(request):
    return render(request, 'home.html', {})

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

# Logout
def logout_user(request):
    logout(request)
    return redirect('home')

def create_post(request):
    if request.method == 'POST':
        form = forms.PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = forms.PostForm()

    return render(request,
                  "create_post.html",
                  {"form": form}
                  )

#shows information about a specific discussion and its posts
def discussion_page(request, id):
    movie = models.Discussion.objects.get(id=id)
    return render(request, "discussion.html", {"movie": movie})

#creating a new discussion
def new_discussion(request):
    if request.method == 'POST':
        form = forms.DiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = forms.DiscussionForm()
    return render(request, 'create_discussion.html', {'form': form})