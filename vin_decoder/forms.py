from django import forms
from django.core.validators import RegexValidator

from .models import NewsletterSubscriber


vin_validator_no_IOQ_letters =RegexValidator(
    regex=r'^[A-HJ-NPR-Z0-9]{17}$',
    message="Invalid VIN: Must be 17 characters and cannot contain I, O, or Q."
)


class InputVinForm(forms.Form):

    """
    Get car vin number and checks it's basic info like model, engine etc.
    """

    vin_number = forms.CharField(
        label="VIN number",
        max_length = 17,
        min_length = 17,
        strip = True,
        required = True,
        validators= [vin_validator_no_IOQ_letters],
        widget= forms.TextInput(attrs={
            'placeholder': "Enter 17-digit VIN",
            'style' : "text-transform: uppercase;" 
        }),
        help_text = "please enter VIN(chasis) number",
        # just for testing purposes, you can remove it later
        initial= "WF0DP3TH6H4123982" 
    )


class NewsletterSubscriberForm(forms.Form):

    """Checks if given email is valid in order to send newsletter"""

    send_email_to= forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder':'name@example.com',
            'class': 'w-full bg-transparent text-white placeholder-white/50 text-sm outline-none border-0',
            })
        )

