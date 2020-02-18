from django.utils import timezone
from backend.connect_database import MongoConnection


class Comment(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("comments")
        self._id = None
        self.user_id = None
        self.message = ""
        self.date_created = timezone.now()

    def __str__(self):
        return self.get_message()[:20]

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def get_date_created(self):
        return self.date_created

    def set_date_created(self, date):
        self.date_created = date
