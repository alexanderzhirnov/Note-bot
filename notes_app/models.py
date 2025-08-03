from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    telegram_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    def __str__(self):
        return self.title