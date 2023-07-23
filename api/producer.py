import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='django')
channel.basic_publish(exchange='',
                      routing_key='django',
                      body='Test message!')
print(" [x] Test message sent'")
connection.close()
