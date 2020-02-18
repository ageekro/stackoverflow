import re
from django.utils import timezone
from backend.connect_database import MongoConnection


class Tag(MongoConnection):
    def __init__(self):
        super().__init__()
        self.get_collection("tags")
        self.__tag = ""
        self.__timestamp = timezone.now()

    def __str__(self):
        return self.get_tag()

    def get_tag(self):
        return self.__tag

    def set_tag(self, tag):
        self.__tag = tag

    def get_timestamp(self):
        return self.__timestamp

    def set_timestamp(self, date):
        self.__timestamp = date

    def get_or_create(self, tag):
        regex_tag = re.compile("^{name}$".format(name=tag), re.IGNORECASE)
        qs = self.collection.find({"tag": regex_tag})
        if qs.count() == 1 or qs.count():
            new_obj = False
            tag_obj = qs.next()
        else:
            data = {
                "tag": tag,
                "timestamp": timezone.now()
            }
            self.collection.insert_one(data)
            qs = self.collection.find({"tag": regex_tag})
            new_obj = True
            tag_obj = qs.next()
        return tag_obj, new_obj


def parsed_tags_receiver(tag_list):
    if len(tag_list) > 0:
        tag = Tag()
        for tag_var in tag_list:
            new_tag, created = tag.get_or_create(tag_var)



