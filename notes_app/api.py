from rest_framework import serializers
from .models import User, Note, Category, Tag

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'telegram_id', 'email']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 
                 'deadline', 'category', 'tags']