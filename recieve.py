import pika
import json
from bson.objectid import ObjectId
from django.conf import settings

from qa.models import Question, QuestionViews

settings.configure()


class Subscriber:
    def __init__(self, exchange):
        self.exchange = exchange
        self.connection = self._create_connection()

    def __del__(self):
        self.connection.close()

    def _create_connection(self):
        param = pika.ConnectionParameters('localhost')
        return pika.BlockingConnection(param)

    def on_message_callback(self, channel, method, properties, body):
        msg = body.decode("utf-8")
        data = json.loads(msg)
        print(" [x] Received %r" % data)
        if data.get("action") == "Add question views":
            self.create_question_views(data)
            self.add_question_views(ObjectId(data.get("question_id")))
            print("add question views done.")

    def create_question_views(self, data):
        question_views = QuestionViews()
        if data.get("user_id") is not None:
            question_views.set_user_id(ObjectId(data.get("user_id")))
        question_views.set_user_ip(data.get("user_ip"))
        question_views.set_question_id(ObjectId(data.get("question_id")))
        context = {
            "user_id": question_views.get_user_id(),
            "user_ip": question_views.get_user_ip(),
            "question_id": question_views.get_question_id(),
            "created_at": question_views.get_created_at()
        }
        question_views.save(context)

    def add_question_views(self, question_id):
        question = Question()
        question.collection.update_one({"_id": question_id}, {"$inc": {"views": 1}})

    def setup(self):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.exchange, exchange_type='fanout')
        result = channel.queue_declare(queue='', durable=True, exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=self.exchange, queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.on_message_callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()


subscriber = Subscriber("question")
subscriber.setup()
