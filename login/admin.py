from django.contrib import admin

from .models import User, Post

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class Post(admin.ModelAdmin):
    pass
