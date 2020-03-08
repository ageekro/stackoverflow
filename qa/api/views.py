import json
from bson.objectid import ObjectId
from bson.errors import InvalidId
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Question, QuestionViews, Answer, Vote
from .serializers import QuestionSerializer, AnswerSerializer
from comments.models import Comment
from accounts.api.utils import user_is_authenticated, get_client_ip
from send import Publisher
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
        question_views = QuestionViews()
        user, user_logged_in = user_is_authenticated(request)
        if user_logged_in:
            user_id = user.get("_id")
            user_ip = get_client_ip(request)
            question_id = instance.get("_id")
            qs = question_views.collection.find({"$and": [{"user_id": user_id}, {"question_id": question_id}]})
            if not qs.count():
                publisher = Publisher("stack")
                data = {"action": "Add question views", "user_id": str(user_id), "user_ip": user_ip,
                        "question_id": str(question_id)}
                publisher.publish(json.dumps(data))
        else:
            user_ip = get_client_ip(request)
            question_id = instance.get("_id")
            qs = question_views.collection.find({"$and": [{"user_ip": user_ip}, {"question_id": question_id}]})
            if not qs.count():
                publisher = Publisher("stack")
                data = {"action": "Add question views", "user_ip": user_ip,
                        "question_id": str(question_id)}
                publisher.publish(json.dumps(data))
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
        # delete all question's comments and answers, question views when question deleted.
        # TODO: delete all question votes
        comment = Comment()
        comments = instance.get("comments")
        for c in comments:
            comment.remove({"_id": ObjectId(c)})
        answer = Answer()
        answer.collection.delete_many({"question_id": instance.get("_id")})
        question_views = QuestionViews()
        question_views.collection.delete_many({"question_id": instance.get("_id")})
        self.question.remove({"_id": instance.get("_id")})


class QuestionVoteUpAPIView(APIView):

    def get_object(self, question, pk):
        try:
            question_id = ObjectId(pk)
        except InvalidId:
            return False
        qs = question.collection.find({"_id": question_id})
        if qs.count() == 1:
            return qs.next()
        else:
            return False

    def get(self, request, pk):
        user, user_logged_in = user_is_authenticated(request)
        if not user_logged_in:
            return Response({"message": "Not Allowed."}, status=400)

        question = Question()
        question_obj = self.get_object(question, pk)
        if not question_obj:
            return Response({"message": "Question object doesn't exists."}, status=400)

        vote = Vote()
        qs = vote.collection.find({"$and": [{"user_id": user.get("_id")}, {"data_id": question_obj.get("_id")}]})
        if not qs.count():
            publisher = Publisher("stack")
            data = {"action": "Add question votes", "user_id": str(user.get("_id")),
                    "data_id": pk, "question_votes": question_obj.get("votes"), "vote_type": 1}
            publisher.publish(json.dumps(data))
            return Response({"vote_added": True})
        else:
            vote_obj = qs.next()
            if vote_obj.get("vote_type") == 1:
                publisher = Publisher("stack")
                data = {"action": "undo question votes",
                        "question_id": pk, "question_votes": question_obj.get("votes"),
                        "vote_id": str(vote_obj.get("_id"))}

                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})
            else:
                # update question vote type to 1 when vote type is -1
                publisher = Publisher("stack")
                data = {"action": "increase question votes", "vote_id": str(vote_obj.get("_id"))}
                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})


class QuestionVoteDownAPIView(APIView):

    def get_object(self, question, pk):
        try:
            question_id = ObjectId(pk)
        except InvalidId:
            return False
        qs = question.collection.find({"_id": question_id})
        if qs.count() == 1:
            return qs.next()
        else:
            return False

    def get(self, request, pk):
        user, user_logged_in = user_is_authenticated(request)
        if not user_logged_in:
            return Response({"message": "Not Allowed."}, status=400)

        question = Question()
        question_obj = self.get_object(question, pk)
        if not question_obj:
            return Response({"message": "Question object doesn't exists."}, status=400)

        vote = Vote()
        qs = vote.collection.find({"$and": [{"user_id": user.get("_id")}, {"data_id": question_obj.get("_id")}]})
        if not qs.count():
            publisher = Publisher("stack")
            data = {"action": "Add question votes", "user_id": str(user.get("_id")),
                    "data_id": pk, "question_votes": question_obj.get("votes"), "vote_type": -1}
            publisher.publish(json.dumps(data))
            return Response({"vote_added": True})
        else:
            vote_obj = qs.next()
            if vote_obj.get("vote_type") == -1:
                publisher = Publisher("stack")
                data = {"action": "undo question votes",
                        "question_id": pk, "question_votes": question_obj.get("votes"),
                        "vote_id": str(vote_obj.get("_id"))}

                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})
            else:
                # update question vote type to -1 when vote type is 1
                publisher = Publisher("stack")
                data = {"action": "decrease question votes", "vote_id": str(vote_obj.get("_id"))}
                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})


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
        # TODO: delete all answer votes
        question = Question()
        comment = Comment()
        comments = instance.get("comments")
        for c in comments:
            comment.remove({"_id": ObjectId(c)})
        self.answer.remove({"_id": instance.get("_id")})
        question.collection.update({"_id": instance.get("question_id")}, {"$inc": {"answers_number": -1}})


class AnswerVoteUpAPIView(APIView):

    def get_object(self, answer, pk):
        try:
            answer_id = ObjectId(pk)
        except InvalidId:
            return False
        qs = answer.collection.find({"_id": answer_id})
        if qs.count() == 1:
            return qs.next()
        else:
            return False

    def get(self, request, pk):
        user, user_logged_in = user_is_authenticated(request)
        if not user_logged_in:
            return Response({"message": "Not Allowed."}, status=400)

        answer = Answer()
        answer_obj = self.get_object(answer, pk)
        if not answer:
            return Response({"message": "Answer object doesn't exists."}, status=400)

        vote = Vote()
        qs = vote.collection.find({"$and": [{"user_id": user.get("_id")}, {"data_id": answer_obj.get("_id")}]})
        if not qs.count():
            publisher = Publisher("stack")
            data = {"action": "Add answer votes", "user_id": str(user.get("_id")),
                    "data_id": pk, "answer_votes": answer_obj.get("votes"), "vote_type": 1}
            publisher.publish(json.dumps(data))
            return Response({"vote_added": True})
        else:
            vote_obj = qs.next()
            if vote_obj.get("vote_type") == 1:
                publisher = Publisher("stack")
                data = {"action": "undo answer votes",
                        "answer_id": pk, "answer_votes": answer_obj.get("votes"),
                        "vote_id": str(vote_obj.get("_id"))}

                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})
            else:
                # update answer vote type to 1 when vote type is -1
                publisher = Publisher("stack")
                data = {"action": "increase answer votes", "vote_id": str(vote_obj.get("_id"))}
                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})


class AnswerVoteDownAPIView(APIView):

    def get_object(self, answer, pk):
        try:
            answer_id = ObjectId(pk)
        except InvalidId:
            return False
        qs = answer.collection.find({"_id": answer_id})
        if qs.count() == 1:
            return qs.next()
        else:
            return False

    def get(self, request, pk):
        user, user_logged_in = user_is_authenticated(request)
        if not user_logged_in:
            return Response({"message": "Not Allowed."}, status=400)

        answer = Answer()
        answer_obj = self.get_object(answer, pk)
        if not answer_obj:
            return Response({"message": "Answer object doesn't exists."}, status=400)

        vote = Vote()
        qs = vote.collection.find({"$and": [{"user_id": user.get("_id")}, {"data_id": answer_obj.get("_id")}]})
        if not qs.count():
            publisher = Publisher("stack")
            data = {"action": "Add answer votes", "user_id": str(user.get("_id")),
                    "data_id": pk, "answer_votes": answer_obj.get("votes"), "vote_type": -1}
            publisher.publish(json.dumps(data))
            return Response({"vote_added": True})
        else:
            vote_obj = qs.next()
            if vote_obj.get("vote_type") == -1:
                publisher = Publisher("stack")
                data = {"action": "undo answer votes",
                        "answer_id": pk, "answer_votes": answer_obj.get("votes"),
                        "vote_id": str(vote_obj.get("_id"))}

                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})
            else:
                # update question vote type to -1 when vote type is 1
                publisher = Publisher("stack")
                data = {"action": "decrease answer votes", "vote_id": str(vote_obj.get("_id"))}
                publisher.publish(json.dumps(data))
                return Response({"vote_added": False})
