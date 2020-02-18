from django.urls import path, re_path

from .views import (QuestionCommentCreateAPIView,
                    CommentListAPIView,
                    CommentDetailAPIView,
                    CommentUpdateAPIView,
                    QuestionCommentDestroyAPIView,
                    AnswerCommentCreateAPIView,
                    AnswerCommentDestroyAPIView
                    )

app_name = 'comments'
urlpatterns = [
    re_path(r'^question/(?P<pk>[\w\d-]+)/$', QuestionCommentCreateAPIView.as_view(), name='comment-question'),
    path('list/', CommentListAPIView.as_view(), name='comment-list'),
    re_path(r'^list/(?P<pk>[\w\d-]+)/$', CommentDetailAPIView.as_view(), name='comment-detail'),
    re_path(r'^(?P<pk>[\w\d-]+)/update/$', CommentUpdateAPIView.as_view(), name='comment-update'),
    re_path(r'^question/(?P<pk>[\w\d-]+)/delete/$', QuestionCommentDestroyAPIView.as_view(), name='q-comment-delete'),
    re_path(r'^answer/(?P<pk>[\w\d-]+)/$', AnswerCommentCreateAPIView.as_view(), name='comment-answer'),
    re_path(r'^answer/(?P<pk>[\w\d-]+)/delete/$', AnswerCommentDestroyAPIView.as_view(), name='a-comment-delete'),
]
