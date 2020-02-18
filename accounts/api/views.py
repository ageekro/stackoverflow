from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .serializers import UserRegisterSerializer, UserDisplaySerializer
from accounts.models import User

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class AuthAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    User = User()

    def post(self, request):
        if not request.session.get("user_id") is None and request.data.get("username") == request.session.get("username"):
            return Response({"detail": "You are already authenticated."}, status=400)
        username = request.data.get("username")
        password = request.data.get("password")
        qs = self.User.collection.find(
            {
                "$or": [{"username": username}, {"email": username}]
            }
        )
        if qs.count() == 1:
            user_obj = qs.next()
            hashed_password = user_obj.get("password")
            if self.User.check_password(hashed_password, password):
                user_id = user_obj.get("_id")
                request.session["user_id"] = str(user_id)
                request.session["username"] = user_obj.get("username")
                self.User.set_id(str(user_id))
                self.User.set_username(username)
                self.User.set_email(user_obj.get("email"))
                self.User.active(user_obj.get("is_active"))
                payload = jwt_payload_handler(self.User)
                token = jwt_encode_handler(payload)
                response = jwt_response_payload_handler(token, self.User, request=None)
                return Response(response)
        return Response({"detail": "Invalid Credentials."}, status=401)


class LogoutAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            del request.session['user_id']
            del request.session['username']
        except KeyError:
            pass
        return Response("You're logged out.")


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserListAPIView(generics.ListAPIView):
    User = User()
    queryset = list(User.collection.find())
    serializer_class = UserDisplaySerializer
    permission_classes = [permissions.AllowAny]

