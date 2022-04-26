from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class User(models.Model):
    #５文字以上
    name = models.CharField(max_length=32, validators=[MinLengthValidator(5)], unique=True)
    mail = models.EmailField(unique=True)
    password = models.CharField(max_length=100, db_index=True)
    info = models.CharField(max_length=400, blank=True)
    is_active = models.BooleanField(default=False)
    def __repr__(self):
        # 主キーとnameを表示させて見やすくする
        # ex) 1: Alice
        return "{}: {}".format(self.pk, self.name)

    __str__ = __repr__  # __str__にも同じ関数を適用

class Tag(models.Model):
    tag_name = models.CharField(max_length=128, unique=True)

class Post(models.Model):
    body = models.TextField()
    tags  = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='entries', on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField('コメント内容')
    post = models.ForeignKey(Post, verbose_name='対象記事', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', verbose_name='親コメント', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)