import hashlib
from django.utils import timezone

from backend.connect_database import MongoConnection


class User(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("users")
        self._id = None
        self.first_name = ""
        self.last_name = ""
        self.username = ""
        self.email = ""
        self.password = ""
        self.is_active = False
        self.date_joined = timezone.now()

    def __str__(self):
        return self.get_username()

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_first_name(self):
        return self.first_name

    def set_first_name(self, first_name):
        self.first_name = first_name

    def get_last_name(self):
        return self.last_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    @staticmethod
    def make_password(password):
        password = password.encode("utf-8")
        hashed = hashlib.md5(password).hexdigest()
        return hashed

    def check_password(self, hashed, password):
        generated_hash = self.make_password(password)
        return hashed == generated_hash

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = self.make_password(password)

    def get_active(self):
        return self.is_active

    def set_active(self):
        self.is_active = True

    def active(self, active):
        self.is_active = active

    def get_date_joined(self):
        return self.date_joined

    def set_date_joined(self, date):
        self.date_joined = date
