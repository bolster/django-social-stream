from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_tweet_model():
    """
    Returns the User model that is active in this project.
    """
    from django.db.models import get_model

    try:
        app_label, model_name = settings.SOCIAL_STREAM_TWEET_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("SOCIAL_STREAM_TWEET_MODEL must be of the form 'app_label.model_name'")
    tweet_model = get_model(app_label, model_name)
    if tweet_model is None:
        raise ImproperlyConfigured("SOCIAL_STREAM_TWEET_MODEL refers to model '%s' that has not been installed" % settings.SOCIAL_STREAM_TWEET_MODEL)
    return tweet_model
