import pika
import sys

from contact_model import Contact


def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange='Sasha_K_exchange_sms', exchange_type='direct')
    channel.queue_declare(queue='sms_queue', durable=True)
    channel.queue_bind(exchange='Sasha_K_exchange_sms', queue='sms_queue', routing_key='sms')

    def send_sms_stub(contact_id):
        print(f"Sending SMS to contact with ID: {contact_id}")
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.message_sent = True
            contact.save()
        except Contact.DoesNotExist:
            print(f"Contact with ID {contact_id} not found.")

    def callback(ch, method, properties, body):
        contact_id = body.decode('utf-8')
        send_sms_stub(contact_id)
        print(f"Received and processed SMS for contact with ID: {contact_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='sms_queue', on_message_callback=callback)

    print(' [*] Waiting for SMS messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
