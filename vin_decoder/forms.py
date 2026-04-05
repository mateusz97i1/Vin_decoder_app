from django import forms
from django.core.validators import RegexValidator


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
        help_text = "please enter VIN(chasis) number"
    )