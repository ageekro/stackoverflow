from bson.objectid import ObjectId
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from django.utils.html import escape
from django.utils.timesince import timesince

from ..models import Question, Answer


jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class QuestionSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(max_length=300)
    body = serializers.CharField(max_length=600)
    tags = serializers.CharField(max_length=100)
    votes = serializers.SerializerMethodField(read_only=True)
    views = serializers.SerializerMethodField(read_only=True)
    answers_number = serializers.SerializerMethodField(read_only=True)
    timesince = serializers.SerializerMethodField(read_only=True)
    display_date = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    def validate_title(self, value):
        title = escape(value)
        return title

    def validate_body(self, value):
        body = escape(value)
        return body

    def get_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("_id"))
        return str(obj.get_id())

    def get_user_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("user_id"))
        return obj.get_user_id()

    def get_votes(self, obj):
        if isinstance(obj, dict):
            return obj.get("votes")
        return obj.get_votes()

    def get_views(self, obj):
        if isinstance(obj, dict):
            return obj.get("views")
        return obj.get_views()

    def get_answers_number(self, obj):
        if isinstance(obj, dict):
            return obj.get("answers_number")
        return obj.get_answers_number()

    def get_timesince(self, obj):
        if isinstance(obj, dict):
            return timesince(obj.get("timestamp")) + " ago"
        return timesince(obj.get_timestamp()) + " ago"

    def get_display_date(self, obj):
        if isinstance(obj, dict):
            local_time = obj.get("timestamp")
        else:
            local_time = obj.get_timestamp()
        return local_time.strftime("%b %d %Y at %I:%M %p")

    def get_comments(self, obj):
        if isinstance(obj, dict):
            return obj.get("comments")
        return obj.get_comments()

    def create(self, validated_data):
        question = Question()
        request = self.context.get("request")
        token = request.headers.get("Authorization").split()[1]
        payload = jwt_decode_handler(token)
        user_id = payload.get("user_id")
        question.set_user_id(user_id)
        question.set_title(validated_data.get("title"))
        question.set_body(validated_data.get("body"))
        question.set_tags(validated_data.get("tags"))
        data = {
            "user_id": ObjectId(user_id),
            "title": question.get_title(),
            "body": question.get_body(),
            "tags": question.get_tags(),
            "votes": question.get_votes(),
            "views": question.get_views(),
            "answers_number": question.get_answers_number(),
            "timestamp": question.get_timestamp(),
            "comments": question.get_comments()
        }
        q_id = question.save(data)
        question.set_id(q_id)
        return question

    def update(self, instance, validated_data):
        question = Question()
        instance["title"] = validated_data.get("title", instance.get("title"))
        instance["body"] = validated_data.get("body", instance.get("body"))
        instance["tags"] = validated_data.get("tags", instance.get("tags"))

        question.set_title(instance.get("title"))
        question.set_body(instance.get("body"))
        question.set_tags(instance.get("tags"))

        data = {
            "title": question.get_title(),
            "body": question.get_body(),
            "tags": question.get_tags(),
        }
        question.update({"_id": instance.get("_id")}, data)

        return instance


class AnswerSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.SerializerMethodField(read_only=True)
    question_id = serializers.SerializerMethodField(read_only=True)
    body = serializers.CharField(max_length=600)
    votes = serializers.SerializerMethodField(read_only=True)
    timesince = serializers.SerializerMethodField(read_only=True)
    display_date = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    def validate_body(self, value):
        body = escape(value)
        return body

    def get_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("_id"))
        return str(obj.get_id())

    def get_user_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("user_id"))
        return obj.get_user_id()

    def get_question_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("question_id"))
        return obj.get_question_id()

    def get_votes(self, obj):
        if isinstance(obj, dict):
            return obj.get("votes")
        return obj.get_votes()

    def get_timesince(self, obj):
        if isinstance(obj, dict):
            return timesince(obj.get("timestamp")) + " ago"
        return timesince(obj.get_timestamp()) + " ago"

    def get_display_date(self, obj):
        if isinstance(obj, dict):
            local_time = obj.get("timestamp")
        else:
            local_time = obj.get_timestamp()
        return local_time.strftime("%b %d %Y at %I:%M %p")

    def get_comments(self, obj):
        if isinstance(obj, dict):
            return obj.get("comments")
        return obj.get_comments()

    def create(self, validated_data):
        answer = Answer()
        question = Question()
        request = self.context.get("request")
        question_id = self.context.get("question_id")
        token = request.headers.get("Authorization").split()[1]
        payload = jwt_decode_handler(token)
        user_id = payload.get("user_id")
        answer.set_user_id(user_id)
        answer.set_body(validated_data.get("body"))
        answer.set_question_id(question_id)
        data = {
            "user_id": ObjectId(user_id),
            "question_id": ObjectId(question_id),
            "body": answer.get_body(),
            "votes": answer.get_votes(),
            "timestamp": answer.get_timestamp(),
            "comments": answer.get_comments()
        }
        answer_id = answer.save(data)
        # increment question's answer number
        question.collection.update({"_id": ObjectId(question_id)}, {"$inc": {"answers_number": 1}})
        answer.set_id(answer_id)
        return answer

    def update(self, instance, validated_data):
        answer = Answer()
        instance["body"] = validated_data.get("body", instance.get("body"))
        answer.set_body(instance.get("body"))

        data = {
            "body": answer.get_body(),
        }
        answer.update({"_id": instance.get("_id")}, data)

        return instance
