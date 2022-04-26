# coding: utf-8

from rest_framework import serializers

from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'info', 'mail', 'password', 'is_active')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer
    class Meta:
        model = Post
        fields = ('body', 'created_at', 'author')