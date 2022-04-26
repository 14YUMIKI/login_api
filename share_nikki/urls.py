# coding: utf-8
from login.views import Login, Something, PostPost, CreateAccount, CompleteAccount
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, include
from login.urls import router as login_router

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # login.urlsをincludeする
    url(r'^api/', include(login_router.urls)),
    path('login/', Login.as_view()),
    path('data/', Something.as_view(), name='some'),
    path('post/', PostPost.as_view(), name='post'),
    path('account/create/', CreateAccount.as_view()),
    path('account/create/complete/<str:token>/', CompleteAccount.as_view()),
]
