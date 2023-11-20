from mongoengine import connect, Document, StringField, BooleanField

connect('hw_8_2', host='mongodb://localhost:27017')

class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True, unique=True)
    phone_number = StringField(required=False)
    message_sent = BooleanField(default=False)
    preferred_contact_method = StringField(choices=('email', 'sms'), default='email')
