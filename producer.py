import pika
from faker import Faker
from contact_model import Contact

fake = Faker()

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='Sasha_K_exchange_email', exchange_type='direct')  # Відокремлено чергу для електронних листів
channel.exchange_declare(exchange='Sasha_K_exchange_sms', exchange_type='direct')  # Відокремлено чергу для SMS
channel.queue_declare(queue='email_queue', durable=True)
channel.queue_bind(exchange='Sasha_K_exchange_email', queue='email_queue', routing_key='email')  # Зв'язано чергу для електронних листів з обмінником
channel.queue_declare(queue='sms_queue', durable=True)
channel.queue_bind(exchange='Sasha_K_exchange_sms', queue='sms_queue', routing_key='sms')  # Зв'язано чергу для SMS з обмінником


def create_tasks():
    for _ in range(10):
        full_name = fake.name()
        email = fake.email()
        phone_number = fake.phone_number()  # Додано генерацію фейкового телефонного номера

        contact = Contact(full_name=full_name, email=email, phone_number=phone_number)
        contact.save()

        message_body = str(contact.id)

        # Визначено спосіб надсилання на основі вибору в моделі
        if contact.preferred_contact_method == 'email':
            channel.basic_publish(exchange='Sasha_K_exchange_email', routing_key='email_queue', body=message_body)
        elif contact.preferred_contact_method == 'sms':
            channel.basic_publish(exchange='Sasha_K_exchange_sms', routing_key='sms_queue', body=message_body)

    print("Messages sent to the email_queue and sms_queue")

    connection.close()


if __name__ == '__main__':
    create_tasks()

