from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from qa.models import Question, QuestionViews


def count_question_views():
    settings.configure()
    time = timezone.now() - timedelta(hours=24)
    question = Question()
    question_views = QuestionViews()
    qs = question_views.collection.find({"created_at": {"$gt": time}})
    for qv in qs:
        question_id = qv.get("question_id")
        question.collection.update_one({"_id": question_id}, {"$inc": {"views": 1}})


count_question_views()
