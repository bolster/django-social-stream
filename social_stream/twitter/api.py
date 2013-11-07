from tastypie import fields
from tastypie.resources import ModelResource

from social_stream.twitter import get_tweet_model


class TweetResource(ModelResource):

    entities = fields.DictField('entities')
    place = fields.DictField('place')
    coordinates = fields.DictField('coordinates')

    class Meta:
        queryset = get_tweet_model().objects.order_by('-created_at')
        excludes = ('raw_data', )
