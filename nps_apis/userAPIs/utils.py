from django.core.mail import EmailMessage
class Util:# create a class for the util functions 
    @staticmethod
    def send_email(data): # create a static method to send email 
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()