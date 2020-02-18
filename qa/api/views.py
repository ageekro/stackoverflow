from bson.objectid import ObjectId
from bson.errors import InvalidId
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from comments.models import Comment
from accounts.api.utils import user_is_authenticated
from backend.permissions import TokenPermission, IsOwnerOrReadOnly, QuestionExistPermission

from django.http import Http404


class QuestionCreateAPIView(generics.CreateAPIView):
    permission_classes = [TokenPermission]
    serializer_class = QuestionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class QuestionListAPIView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        question = Question()
        return list(question.collection.find().sort("timestamp", -1))


class QuestionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = QuestionSerializer

    def get_object(self):
        question = Question()
        try:
            question_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = question.collection.find({"_id": question_id})
        if qs.count() == 1:
            question_obj = qs.next()
            return question_obj
        else:
            raise Http404("No question matches the given query.")

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        user, user_logged_in = user_is_authenticated(request)
        # if user_logged_in:
        #     # user id
        # else:
        #     #ip
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class QuestionUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    serializer_class = QuestionSerializer

    def get_object(self):
        question = Question()
        try:
            question_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = question.collection.find({"_id": question_id})
        if qs.count() == 1:
            question_obj = qs.next()
            self.check_object_permissions(self.request, question_obj)
            return question_obj
        else:
            raise Http404("No question matches the given query.")


class QuestionDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    question = Question()

    def get_object(self):
        try:
            question_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = self.question.collection.find({"_id": question_id})
        if qs.count() == 1:
            question_obj = qs.next()
            self.check_object_permissions(self.request, question_obj)
            return question_obj
        else:
            raise Http404("No question matches the given query.")

    def perform_destroy(self, instance):
        # delete all question's comments and answers when question deleted.
        comment = Comment()
        comments = instance.get("comments")
        for c in comments:
            comment.remove({"_id": ObjectId(c)})
        answer = Answer()
        answer.collection.delete_many({"question_id": instance.get("_id")})
        self.question.remove({"_id": instance.get("_id")})


class QuestionViewsAPIView(APIView):

    def get(self, request, pk):
        question = Question()
        try:
            question_id = ObjectId(pk)
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = question.collection.find({"_id": question_id})
        if qs.count() == 1:
            question.collection.update({"_id": ObjectId(question_id)}, {"$inc": {"views": 1}})
            return Response({"viewed": True})
        return Response({'message': "question object doesn't exists."}, status=400)


class AnswerCreateAPIView(generics.CreateAPIView):
    permission_classes = [TokenPermission, QuestionExistPermission]
    serializer_class = AnswerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        try:
            question_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        self.check_object_permissions(self.request, question_id)
        context["question_id"] = self.kwargs.get("pk")
        return context


class AnswerListAPIView(generics.ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        answer = Answer()
        return list(answer.collection.find().sort("timestamp", -1))


class AnswerDetailAPIView(generics.RetrieveAPIView):
    serializer_class = AnswerSerializer

    def get_object(self):
        answer = Answer()
        try:
            answer_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = answer.collection.find({"_id": answer_id})
        if qs.count() == 1:
            answer_obj = qs.next()
            return answer_obj
        else:
            raise Http404("No question matches the given query.")


class AnswerUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    serializer_class = AnswerSerializer

    def get_object(self):
        answer = Answer()
        try:
            answer_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = answer.collection.find({"_id": answer_id})
        if qs.count() == 1:
            answer_obj = qs.next()
            self.check_object_permissions(self.request, answer_obj)
            return answer_obj
        else:
            raise Http404("No question matches the given query.")


class AnswerDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    answer = Answer()

    def get_object(self):
        try:
            answer_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("question id is not valid.")
        qs = self.answer.collection.find({"_id": answer_id})
        if qs.count() == 1:
            answer_obj = qs.next()
            self.check_object_permissions(self.request, answer_obj)
            return answer_obj
        else:
            raise Http404("No question matches the given query.")

    def perform_destroy(self, instance):
        # delete all answers's comment when answer deleted.
        question = Question()
        comment = Comment()
        comments = instance.get("comments")
        for c in comments:
            comment.remove({"_id": ObjectId(c)})
        self.answer.remove({"_id": instance.get("_id")})
        question.collection.update({"_id": instance.get("question_id")}, {"$inc": {"answers_number": -1}})
