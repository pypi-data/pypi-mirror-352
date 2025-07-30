from enum import Enum

import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import Mail

EMAIL_SENDER = settings.SENDGRID_EMAIL_SENDER
EMAIL_COPY = settings.SENDGRID_EMAIL_COPY


class SendEmailError(Exception):
    pass


class EmailTemplates(Enum):
    contact_form = settings.SENDGRID_TEMPLATE_CONTACT_FORM
    basket_user = settings.SENDGRID_TEMPLATE_BASKET_USER
    basket_admin = settings.SENDGRID_TEMPLATE_BASKET_ADMIN


def send_email_with_sendgrid(*, to_emails, data, template_id, with_copy, bcc):
    sendgrid_api_key = settings.SENDGRID_API_KEY
    if sendgrid_api_key is None:
        return
    sendgrid_client = sendgrid.SendGridAPIClient(sendgrid_api_key)
    message = Mail(
        from_email=EMAIL_SENDER,
        to_emails=to_emails,
    )
    message.dynamic_template_data = data
    message.template_id = template_id
    if with_copy:
        message.add_bcc(EMAIL_COPY)
    if bcc:
        message.add_bcc(bcc)
    response = sendgrid_client.send(message)
    if response.status_code != 202:
        raise SendEmailError


def send_email(
    users,
    *,
    email_template,
    data=None,
    with_copy=True,
    bcc=None,
):
    if data is None:
        data = {}
    if type(users) is list:
        to_emails = [user if type(user) is str else user.email for user in users]
    else:
        to_emails = [users if type(users) is str else users.email]
    send_email_with_sendgrid(
        to_emails=to_emails,
        data=data,
        template_id=email_template.value,
        with_copy=with_copy,
        bcc=bcc,
    )
