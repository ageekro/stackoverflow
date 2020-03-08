import pika
import json
from bson.objectid import ObjectId
from django.conf import settings

from qa.models import Question, QuestionViews, Answer, Vote

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

        elif data.get("action") == "Add question votes":
            vote_id = self.create_vote(data)
            question = Question()
            question_votes = data.get("question_votes")
            question_votes.append(str(vote_id))
            context = {
                "votes": question_votes
            }
            question.update({"_id": ObjectId(data.get("data_id"))}, context)
            print("add question votes done.")

        elif data.get("action") == "undo question votes":
            vote_id = ObjectId(data.get("vote_id"))
            question = Question()
            question_votes = data.get("question_votes")
            question_votes.remove(str(vote_id))
            context = {
                "votes": question_votes
            }
            question.update({"_id": ObjectId(data.get("question_id"))}, context)
            vote = Vote()
            vote.remove({"_id": vote_id})
            print("undo question votes done.")

        elif data.get("action") == "increase question votes":
            vote = Vote()
            context = {
                "vote_type": 1
            }
            vote.update({"_id": ObjectId(data.get("vote_id"))}, context)
            print("increase question votes done.")

        elif data.get("action") == "decrease question votes":
            vote = Vote()
            context = {
                "vote_type": -1
            }
            vote.update({"_id": ObjectId(data.get("vote_id"))}, context)
            print("decrease question votes done.")

        elif data.get("action") == "Add answer votes":
            vote_id = self.create_vote(data)
            answer = Answer()
            answer_votes = data.get("answer_votes")
            answer_votes.append(str(vote_id))
            context = {
                "votes": answer_votes
            }
            answer.update({"_id": ObjectId(data.get("data_id"))}, context)
            print("add answer votes done.")

        elif data.get("action") == "undo answer votes":
            vote_id = ObjectId(data.get("vote_id"))
            answer = Answer()
            answer_votes = data.get("answer_votes")
            answer_votes.remove(str(vote_id))
            context = {
                "votes": answer_votes
            }
            answer.update({"_id": ObjectId(data.get("answer_id"))}, context)
            vote = Vote()
            vote.remove({"_id": vote_id})
            print("undo answer votes done.")

        elif data.get("action") == "increase answer votes":
            vote = Vote()
            context = {
                "vote_type": 1
            }
            vote.update({"_id": ObjectId(data.get("vote_id"))}, context)
            print("increase answer votes done.")

        elif data.get("action") == "decrease answer votes":
            vote = Vote()
            context = {
                "vote_type": -1
            }
            vote.update({"_id": ObjectId(data.get("vote_id"))}, context)
            print("decrease answer votes done.")

    @staticmethod
    def create_question_views(data):
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

    @staticmethod
    def add_question_views(question_id):
        question = Question()
        question.collection.update_one({"_id": ObjectId(question_id)}, {"$inc": {"views": 1}})

    @staticmethod
    def create_vote(data):
        vote = Vote()
        vote.set_user_id(ObjectId(data.get("user_id")))
        vote.set_data_id(ObjectId(data.get("data_id")))
        vote.set_vote_type(data.get("vote_type"))
        context = {
            "user_id": vote.get_user_id(),
            "data_id": vote.get_data_id(),
            "vote_type": vote.get_vote_type(),
            "created_at": vote.get_created_at()
        }
        vote_id = vote.save(context)
        return vote_id

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


subscriber = Subscriber("stack")
subscriber.setup()
