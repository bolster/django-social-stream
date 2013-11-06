from tastypie import fields
from tastypie.resources import ModelResource

from .models import *


class TweetResource(ModelResource):

    entities = fields.DictField('entities')
    place = fields.DictField('place')
    coordinates = fields.DictField('coordinates')

    class Meta:
        queryset = Tweet.objects.order_by('-created_at')
        excludes = ('raw_data', )
