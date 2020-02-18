import datetime
from bson.objectid import ObjectId
from django.utils import timezone
from rest_framework_jwt.settings import api_settings

from ..models import User

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX
expire_delta = api_settings.JWT_REFRESH_EXPIRATION_DELTA


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "username": user.get_username(),
        "expires": timezone.now() + expire_delta - datetime.timedelta(seconds=200)
    }


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        print(x_forwarded_for)
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


def user_is_authenticated(request):
    # Check user logged in and return user object
    user = User()
    output = None, False
    if request.headers.get("Authorization"):
        return output
    headers = request.headers.get("Authorization").split()
    if len(headers) == 2 and headers[0] == jwt_auth_header_prefix:
        return output

    payload = jwt_decode_handler(headers[1])
    user_id = payload.get("user_id")
    user_object_id = ObjectId(user_id)
    qs = user.collection.find({"_id": user_object_id})
    if qs.count() == 1:
        output = qs.next(), True
        return output
    return output

