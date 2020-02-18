from bson.objectid import ObjectId
from bson.errors import InvalidId
from rest_framework import generics
from backend.permissions import TokenPermission, IsOwnerOrReadOnly, QuestionExistPermission, AnswerExistPermission
from django.http import Http404

from qa.models import Question, Answer

from .serializers import CommentSerializer
from..models import Comment


class QuestionCommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [TokenPermission, QuestionExistPermission]
    serializer_class = CommentSerializer

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


class CommentListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        comment = Comment()
        return list(comment.collection.find().sort("timestamp", -1))


class CommentDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer

    def get_object(self):
        comment = Comment()
        try:
            comment_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("comment id is not valid.")
        qs = comment.collection.find({"_id": comment_id})
        if qs.count() == 1:
            comment_obj = qs.next()
            return comment_obj
        else:
            raise Http404("No comment matches the given query.")


class CommentUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    serializer_class = CommentSerializer

    def get_object(self):
        comment = Comment()
        try:
            comment_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("comment id is not valid.")
        qs = comment.collection.find({"_id": comment_id})
        if qs.count() == 1:
            comment_obj = qs.next()
            self.check_object_permissions(self.request, comment_obj)
            return comment_obj
        else:
            raise Http404("No comment matches the given query.")


class QuestionCommentDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    comment = Comment()

    def get_object(self):
        try:
            comment_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("comment id is not valid.")
        qs = self.comment.collection.find({"_id": comment_id})
        if qs.count() == 1:
            comment_obj = qs.next()
            self.check_object_permissions(self.request, comment_obj)
            return comment_obj
        else:
            raise Http404("No comment matches the given query.")

    def perform_destroy(self, instance):
        question = Question()
        qs = question.collection.find({"comments": {"$all": [str(instance.get("_id"))]}})
        if qs.count() == 1:
            question_obj = qs.next()
            comments = question_obj.get("comments")
            # delete comment id from question comment list
            comments.remove(str(instance.get("_id")))
            data = {
                "comments": comments
            }
            question.update({"_id": question_obj.get("_id")}, data)
            self.comment.remove({"_id": instance.get("_id")})


class AnswerCommentCreateAPIView(generics.CreateAPIView):
    permission_classes = [TokenPermission, AnswerExistPermission]
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        try:
            answer_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("answer id is not valid.")
        self.check_object_permissions(self.request, answer_id)
        context["answer_id"] = self.kwargs.get("pk")
        return context


class AnswerCommentDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [TokenPermission, IsOwnerOrReadOnly]
    comment = Comment()

    def get_object(self):
        try:
            comment_id = ObjectId(self.kwargs.get('pk'))
        except InvalidId:
            raise Http404("comment id is not valid.")
        qs = self.comment.collection.find({"_id": comment_id})
        if qs.count() == 1:
            comment_obj = qs.next()
            self.check_object_permissions(self.request, comment_obj)
            return comment_obj
        else:
            raise Http404("No comment matches the given query.")

    def perform_destroy(self, instance):
        answer = Answer()
        qs = answer.collection.find({"comments": {"$all": [str(instance.get("_id"))]}})
        if qs.count() == 1:
            answer_obj = qs.next()
            comments = answer_obj.get("comments")
            # delete comment id from answer comment list
            comments.remove(str(instance.get("_id")))
            data = {
                "comments": comments
            }
            answer.update({"_id": answer_obj.get("_id")}, data)
            self.comment.remove({"_id": instance.get("_id")})
