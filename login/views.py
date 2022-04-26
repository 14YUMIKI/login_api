# coding: utf-8

import django_filters
from rest_framework import viewsets, filters
from .models import User, Post
from .serializer import UserSerializer, PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from share_nikki.utils.auth import NormalAuthentication
from share_nikki.utils.auth import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.core import signing
import time
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class Login(APIView):
    authentication_classes = [NormalAuthentication]
    #authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request, *args, **kwargs):
        return Response({"token": request.user})
        #return Response({"token": request.data["password"]})

class Something(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        authorized_user = request.user
        msg = "ID'" + str(authorized_user.pk) + "' is logged in."
        return Response({"data": msg})

class PostPost(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        authorized_user = request.user
        try:
            post = Post()
            post.body = request.data["post"]
            post.author = authorized_user
            post.tags = request.data["tags"]
            post.save()
        except:
            return Response({"message": "Data format is not valid"})

        return Response({"message": "Succeeded"})



class CreateAccount(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        try:
            account_name = request.data["name"]
            account_password = request.data["password"]
            account_email = request.data["email"]
        except:
            return Response({"message": "Data format is not valid"})

        

        #Default message
        message = "Failed"

        try:
            new_user = User()
            new_user.name = account_name
            new_user.password = make_password(account_password)
            new_user.mail = account_email
        except:
            return Response({"message": "failed making new account"})
        

        try:
            #Check if email is alredy used
            exist_user = User.objects.filter(mail=account_email).first()
            if exist_user is not None:
                if exist_user.is_active is True:
                    send_mail('Email Verification', 'This email address is already used.', 'Share_Nikki', [account_email], fail_silently=False)
                    return Response({"message": "Success"})
                else:
                    exist_user.delete()
            #validate the posted data 
            #I don't know why but this method works and never raise error and skip excet: ...
            new_user.full_clean()
            new_user.is_active = False
            #valid for 1 hour
            timestamp = int(time.time()) + 60*60
            one_time_token = signing.dumps({'email': account_email, 'exp_date': timestamp})
            url = 'http://localhost:8000/account/create/complete/' + one_time_token + '/'
            main_text = (
            "Thanks for your registration!\n"
            "Please click the link below and complete verification of email.\n"
            + url)
            send_mail('Email Verification', main_text, 'Share_Nikki', [account_email], fail_silently=False)
            new_user.save()
            message = "Success"
        except:
            messsage = "Failed"
        
        return Response({"message": message})

class CompleteAccount(APIView):
    def get(self, request, *args, **kwargs):
        message = "DEFAULT"
        one_time_token = self.kwargs.get('token',None)
        if one_time_token is not None:
            data = signing.loads(one_time_token)
            unverifyed_email = data['email']
            exp_date = data['exp_date']
            if int(time.time()) < exp_date:
                try:
                    unverifyed_user = User.objects.filter(mail=unverifyed_email).first()
                    unverifyed_user.is_active = True
                    unverifyed_user.save()
                    message = "success"
                except Exception as e:
                    message = e
            else:
                message = "This token is expired"
        return Response({"message": message})
