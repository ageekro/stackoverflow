import pika


class Publisher:
    def __init__(self, exchange):
        self.exchange = exchange

    def publish(self, message):
        connection = self.create_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange, exchange_type="fanout")
        channel.basic_publish(exchange=self.exchange, routing_key="", body=message,
                              properties=pika.BasicProperties(delivery_mode=2))
        print(" [x] Sent %r" % message)
        connection.close()

    # Create new connection
    def create_connection(self):
        param = pika.ConnectionParameters('localhost')
        return pika.BlockingConnection(param)
