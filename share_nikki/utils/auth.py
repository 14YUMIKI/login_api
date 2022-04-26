import time
import jwt
from share_nikki.settings import SECRET_KEY
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework import authentication
from login.models import User
from django.contrib.auth.hashers import make_password, check_password


class NormalAuthentication(BaseAuthentication):
    def authenticate(self, request):
        name_or_email = request.data['name']
        password = request.data['password']
        user_obj = User.objects.filter(name=name_or_email).first()
        #　もしメールでログインしようとしていたら
        if not user_obj:
            user_obj = User.objects.filter(mail=name_or_email).first()
        # ユーザーが存在しなければ
        if not user_obj:
            raise exceptions.AuthenticationFailed('Failed to login')
        # ユーザーが存在してパスワードが合わなければ
        elif not check_password(password, user_obj.password):
            raise exceptions.AuthenticationFailed('Failed to login')
        # ユーザーが存在してパスワードがあっていてメール認証がまだであれば
        elif user_obj.is_active == False:
            raise exceptions.AuthenticationFailed('Failed to login')
        token = generate_jwt(user_obj)
        return (token, None)

    def authenticate_header(self, request):
        pass

# 先程インストールしたjwtライブラリでTokenを生成します
# Tokenの内容はユーザーの情報とタイムアウトが含まれてます
# タイムアウトのキーはexpであることは固定してます
# ドキュメント: https://pyjwt.readthedocs.io/en/latest/usage.html?highlight=exp
def generate_jwt(user):
    #１週間後に無効
    timestamp = int(time.time()) + 60*60*24*7
    return jwt.encode(
        {"userid": user.pk, "name": user.name, "info": user.info, "exp": timestamp},
        SECRET_KEY)

class JWTAuthentication(BaseAuthentication):
    keyword = 'JWT'
    model = None

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = "Authorization failed"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Authorization failed"
            raise exceptions.AuthenticationFailed(msg)

        try:
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
            userid = jwt_info.get("userid")
            try:
                user = User.objects.get(pk=userid)
                user.is_authenticated = True
                return (user, jwt_token)
            except:
                msg = "user does not exist"
                raise exceptions.AuthenticationFailed(msg)
        except jwt.ExpiredSignatureError:
            msg = "this token is expired"
            raise exceptions.AuthenticationFailed(msg)

    def authenticate_header(self, request):
        pass