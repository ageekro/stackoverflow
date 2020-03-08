from django.urls import path, re_path

from .views import (QuestionCreateAPIView,
                    QuestionListAPIView,
                    QuestionDetailAPIView,
                    QuestionUpdateAPIView,
                    QuestionDestroyAPIView,
                    QuestionVoteUpAPIView,
                    QuestionVoteDownAPIView,
                    AnswerCreateAPIView,
                    AnswerListAPIView,
                    AnswerDetailAPIView,
                    AnswerUpdateAPIView,
                    AnswerDestroyAPIView,
                    AnswerVoteUpAPIView,
                    AnswerVoteDownAPIView,
                    SearchAPIView
                    )

app_name = 'qa'
urlpatterns = [
    path('search/', SearchAPIView.as_view(), name="search"),
    path('question/ask/', QuestionCreateAPIView.as_view(), name="question-create"),
    path('questions/', QuestionListAPIView.as_view(), name='question-list'),
    re_path(r'^questions/(?P<pk>[\w\d-]+)/$', QuestionDetailAPIView.as_view(), name='question-detail'),
    re_path(r'^questions/(?P<pk>[\w\d-]+)/update/$', QuestionUpdateAPIView.as_view(), name='question-update'),
    re_path(r'^questions/(?P<pk>[\w\d-]+)/delete/$', QuestionDestroyAPIView.as_view(), name='question-delete'),
    re_path(r'^questions/(?P<pk>[\w\d-]+)/vote/up/$', QuestionVoteUpAPIView.as_view(), name='question-vote-up'),
    re_path(r'^questions/(?P<pk>[\w\d-]+)/vote/down/$', QuestionVoteDownAPIView.as_view(), name='question-vote-down'),
    re_path(r'^answer/(?P<pk>[\w\d-]+)/$', AnswerCreateAPIView.as_view(), name="answer-create"),
    path('answers/', AnswerListAPIView.as_view(), name='answer-list'),
    re_path(r'^answers/(?P<pk>[\w\d-]+)/$', AnswerDetailAPIView.as_view(), name='answer-detail'),
    re_path(r'^answers/(?P<pk>[\w\d-]+)/update/$', AnswerUpdateAPIView.as_view(), name='answer-update'),
    re_path(r'^answers/(?P<pk>[\w\d-]+)/delete/$', AnswerDestroyAPIView.as_view(), name='answer-delete'),
    re_path(r'^answers/(?P<pk>[\w\d-]+)/vote/up/$', AnswerVoteUpAPIView.as_view(), name='answer-vote-up'),
    re_path(r'^answers/(?P<pk>[\w\d-]+)/vote/down/$', AnswerVoteDownAPIView.as_view(), name='answer-vote-down'),
]
