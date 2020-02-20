from bson.objectid import ObjectId
from rest_framework import permissions
from rest_framework_jwt.settings import api_settings

from accounts.models import User
from qa.models import Question, Answer

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX


class TokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = User()
        if not request.headers.get("Authorization"):
            return False
        headers = request.headers.get("Authorization").split()
        if not (len(headers) == 2 and headers[0] == jwt_auth_header_prefix):
            return False

        payload = jwt_decode_handler(headers[1])
        user_id = payload.get("user_id")
        user_object_id = ObjectId(user_id)
        qs = user.collection.find({"_id": user_object_id})
        if qs.count() == 1:
            return True
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        payload = jwt_decode_handler(request.headers.get("Authorization").split()[1])
        user_id = payload.get("user_id")
        if str(obj.get("user_id")) == user_id:
            return True
        return False


class QuestionExistPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        question_id = obj
        question = Question()
        qs = question.collection.find({"_id": ObjectId(question_id)})
        if qs.count() == 1:
            return True
        return False


class AnswerExistPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        answer_id = obj
        answer = Answer()
        qs = answer.collection.find({"_id": ObjectId(answer_id)})
        if qs.count() == 1:
            return True
        return False
