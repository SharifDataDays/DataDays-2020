from rest_framework import serializers
from blog.models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name_en', 'name_fa', 'color']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['writer_name', 'text', 'date', 'email', 'shown']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ['comments', 'tags', 'date', 'image', 'title_en', 'title_fa', 'text_en', 'text_fa']


class PostDescriptionSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ['comments', 'tags', 'date', 'image', 'title_en', 'title_fa', 'description_en', 'description_fa']
