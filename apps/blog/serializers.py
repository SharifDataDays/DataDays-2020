from rest_framework import serializers
from django.conf import settings

from apps.blog.models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name_en', 'name_fa', 'color']


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), allow_null=True)

    class Meta:
        model = Comment
        fields = ['user', 'text', 'date', 'reply_to', 'post']
        read_only_fields = ['replies']

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    num_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['tags', 'num_comments', 'date', 'image',
                  'title_en', 'title_fa', 'text_en', 'text_fa',
                  'description_en', 'description_fa']

    def get_num_comments(self, obj):
        return obj.comments.count()


class PostDescriptionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'tags', 'date', 'image', 'title_en',
                  'title_fa', 'description_en', 'description_fa']
