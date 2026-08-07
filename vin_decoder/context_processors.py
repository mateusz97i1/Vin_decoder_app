from .forms import NewsletterSubscriberForm

def newsletter_form(request):
    """Shares newsletter for to all views and templates"""

    return{'email_form':NewsletterSubscriberForm()}