import re
from django.utils import timezone
from backend.connect_database import MongoConnection
from tags.models import parsed_tags_receiver


class Question(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("questions")
        self._id = None
        self.user_id = None
        self.title = ""
        self.body = ""
        self.tags = []
        self.votes = []
        self.views = 0
        self.answers_number = 0
        self.timestamp = timezone.now()
        self.comments = []

    def __str__(self):
        return self.get_title()

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_body(self):
        return self.body

    def set_body(self, body):
        self.body = body

    def get_tags(self):
        return self.tags

    def set_tags(self, tags):
        tag_regex = r'(?P<tag>[\w\d-]+)'
        tag_list = re.findall(tag_regex, tags)
        [self.tags.append(x) for x in tag_list if x not in self.tags]

    def get_votes(self):
        return self.votes

    def set_votes(self, votes):
        self.votes.extend(votes)

    def get_views(self):
        return self.views

    def set_views(self, views):
        self.views = views

    def get_answers_number(self):
        return self.answers_number

    def set_answers_number(self, number):
        self.answers_number = number

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, date):
        self.timestamp = date

    def get_comments(self):
        return self.comments

    def set_comments(self, comment_ids):
        self.comments.extend(comment_ids)

    def save(self, obj):
        if len(obj) > 0 and isinstance(obj, dict):
            tag_save_receiver(obj)
            insert_id = self.collection.insert_one(obj).inserted_id
            return insert_id


def tag_save_receiver(instance):
    parsed_tags_receiver(instance.get("tags"))


class QuestionViews(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("questions_views")
        self._id = None
        self.user_id = None
        self.user_ip = None
        self.question_id = None
        self.created_at = timezone.now()

    def __str__(self):
        return self.get_user_id()

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_ip(self):
        return self.user_ip

    def set_user_ip(self, user_ip):
        self.user_ip = user_ip

    def get_question_id(self):
        return self.question_id

    def set_question_id(self, question_id):
        self.question_id = question_id

    def get_created_at(self):
        return self.created_at

    def set_created_at(self, date):
        self.created_at = date


class Answer(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("answers")
        self._id = None
        self.user_id = None
        self.question_id = None
        self.body = ""
        self.votes = []
        self.update_time = None
        self.timestamp = timezone.now()
        self.comments = []

    def __str__(self):
        return self.get_body()[:20]

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_question_id(self):
        return self.question_id

    def set_question_id(self, question_id):
        self.question_id = question_id

    def get_body(self):
        return self.body

    def set_body(self, body):
        self.body = body

    def get_votes(self):
        return self.votes

    def set_votes(self, votes):
        self.votes.extend(votes)

    def get_update_time(self):
        return self.update_time

    def set_update_time(self, date):
        self.update_time = date

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, date):
        self.timestamp = date

    def get_comments(self):
        return self.comments

    def set_comments(self, comment_ids):
        self.comments.extend(comment_ids)


class Vote(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("vote")
        self._id = None
        self.user_id = None
        self.data_id = None
        self.vote_type = None
        self.created_at = timezone.now()

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_data_id(self):
        return self.data_id

    def set_data_id(self, data_id):
        self.data_id = data_id

    def get_vote_type(self):
        return self.vote_type

    def set_vote_type(self, vote_type):
        self.vote_type = vote_type

    def get_created_at(self):
        return self.created_at

    def set_created_at(self, date):
        self.created_at = date
