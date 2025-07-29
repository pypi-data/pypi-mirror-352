from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class DjangoPuzzleConfig(AppConfig):
    name = "prune_captcha"

    def ready(self):
        if not hasattr(settings, "PUZZLE_IMAGE_STATIC_PATH"):
            raise ImproperlyConfigured(
                "prune_captcha: vous devez définir PUZZLE_IMAGE_STATIC_PATH dans settings.py"
            )
        if not hasattr(settings, "PUZZLE_HINT_TEXT"):
            raise ImproperlyConfigured(
                "prune_captcha: vous devez définir PUZZLE_HINT_TEXT  dans settings.py"
            )
