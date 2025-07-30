import re

from django import forms


def clean_phone(phone: str):
    if phone and not re.match(r"^[\d\+\- \(\)]{6,20}$", phone):
        raise forms.ValidationError("Numéro invalide")
    return phone
