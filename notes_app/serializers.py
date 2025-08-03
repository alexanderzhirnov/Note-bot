from rest_framework import serializers
from .models import Note, Category, Tag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class NoteSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 
                 'deadline', 'category', 'tags']