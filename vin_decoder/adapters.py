from allauth.account.adapter import DefaultAccountAdapter

from .tasks import send_async_email

class AsyncAccountAdapter(DefaultAccountAdapter):
    "Override base allauth send mail function to send async mail using celery task"

    def send_mail(self, template_prefix, email, context):


        msg= self.render_mail(template_prefix, email, context)

        #flat dictionary for celery
        email_payload = {
            'subject': msg.subject,
            'body': msg.body,
            'from_email': msg.from_email,
            'to': msg.to,
            'cc': msg.cc,
            'bcc': msg.bcc,
            'html_body': msg.alternatives[0][0] if msg.alternatives else None
        }

        #send to celery task
        send_async_email.delay(email_data = email_payload)
