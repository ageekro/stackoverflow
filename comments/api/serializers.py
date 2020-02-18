from bson.objectid import ObjectId
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from django.utils.html import escape
from django.utils.timesince import timesince

from ..models import Comment
from qa.models import Question, Answer

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class CommentSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.SerializerMethodField(read_only=True)
    message = serializers.CharField(max_length=300)
    timesince = serializers.SerializerMethodField(read_only=True)
    display_date = serializers.SerializerMethodField(read_only=True)

    def validate_message(self, value):
        message = escape(value)
        return message

    def get_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("_id"))
        return str(obj.get_id())

    def get_user_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("user_id"))
        return obj.get_user_id()

    def get_timesince(self, obj):
        if isinstance(obj, dict):
            return timesince(obj.get("date_created")) + " ago"
        return timesince(obj.get_date_created()) + " ago"

    def get_display_date(self, obj):
        if isinstance(obj, dict):
            local_time = obj.get("date_created")
        else:
            local_time = obj.get_date_created()
        return local_time.strftime("%b %d %Y at %I:%M %p")

    def create(self, validated_data):
        comment = Comment()
        request = self.context.get("request")
        token = request.headers.get("Authorization").split()[1]
        payload = jwt_decode_handler(token)
        user_id = payload.get("user_id")
        comment.set_user_id(user_id)
        comment.set_message(validated_data.get("message"))
        data = {
            "user_id": ObjectId(user_id),
            "message": comment.get_message(),
            "date_created": comment.get_date_created(),
        }
        c_id = comment.save(data)
        comment.set_id(c_id)
        # Add comment's id to question comment list
        if self.context.get("question_id"):
            question = Question()
            qs = question.collection.find({"_id": ObjectId(self.context.get("question_id"))})
            if qs.count() == 1:
                question_obj = qs.next()
                comments_list = question_obj.get("comments")
                comments_list.append(str(comment.get_id()))

                data = {
                    "comments": comments_list
                }
                question.update({"_id": question_obj.get("_id")}, data)
        # Add comment's id to answer comment list
        elif self.context.get("answer_id"):
            answer = Answer()
            qs = answer.collection.find({"_id": ObjectId(self.context.get("answer_id"))})
            if qs.count() == 1:
                answer_obj = qs.next()
                comments_list = answer_obj.get("comments")
                comments_list.append(str(comment.get_id()))

                data = {
                    "comments": comments_list
                }
                answer.update({"_id": answer_obj.get("_id")}, data)
        return comment

    def update(self, instance, validated_data):
        comment = Comment()
        instance["message"] = validated_data.get("message", instance.get("message"))

        comment.set_message(instance.get("message"))

        data = {
            "message": comment.get_message()
        }

        comment.update({"_id": instance.get("_id")}, data)

        return instance
