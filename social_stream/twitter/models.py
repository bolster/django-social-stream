import datetime
import json

from celery_pipelines import *

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.gdal.srs import SpatialReference
from django.utils.timezone import utc

from jsonfield import JSONField

from social_stream.twitter import get_tweet_model

from autoslug.fields import AutoSlugField

try:
    from django.contrib.gis.gdal.geometries import OGRGeometry
    LOCATION_CALC_ENABLED = True
except:
    print "GDAL not enabled"
    LOCATION_CALC_ENABLED = False


__ALL__ = ["Tweet", "TwitterUser", "StreamAccount", "Stream", "TrackedTerm", "FollowedUser", "FollowedLocation"]


TWEET_PIPELINES = getattr(settings, "SOCIAL_STREAM_TWITTER_PIPELINES", [])


def parse_twitter_date(date_str):
    dt = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y')
    dt = dt.replace(tzinfo=utc)
    return dt


def parse_tweet_obj(tweet_obj):
    data = {
        'id': tweet_obj['id_str'],
        'in_reply_to_screen_name': tweet_obj['in_reply_to_screen_name'],
        'in_reply_to_status_id': tweet_obj['in_reply_to_status_id_str'],
        'in_reply_to_user_id': tweet_obj['in_reply_to_user_id'],
        'place': tweet_obj['place'] or {},
        'coordinates': tweet_obj['coordinates'] or {},
        'entities': tweet_obj['entities'] or {},
        'retweet_count': int(tweet_obj['retweet_count']),
        'favorite_count': int(tweet_obj['favorite_count']),
        'text': tweet_obj['text'],
        'created_at': parse_twitter_date(tweet_obj['created_at']),
        'raw_data': tweet_obj
    }

    return data


def parse_twitter_user_obj(user_obj):
    data = {
        'id': user_obj['id_str'],
        'name': user_obj['name'],
        'screen_name': user_obj['screen_name'],
        'description': user_obj['description'],
        'profile_image_url': user_obj['profile_image_url'],
        'favourites_count': int(user_obj['favourites_count']),
        'followers_count': int(user_obj['followers_count']),
        'friends_count': int(user_obj['friends_count']),
        'verified': True if user_obj['verified'] == "true" else False,
        'raw_data': user_obj
    }

    return data


class StreamAccountManager(models.Manager):
    def get_default_account(self):
        account = None

        try:
            account = self.get(default=True)
        except StreamAccount.DoesNotExist:
            if self.count() > 0:
                account = self.all()[0]

        return account


class StreamAccount(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")

    oauth_token = models.CharField(max_length=1000)
    oauth_token_secret = models.CharField(max_length=1000)

    default = models.BooleanField(default=False)

    objects = StreamAccountManager()

    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.slug)

    def auth_data(self):
        return self.oauth_token, self.oauth_token_secret


class Stream(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")

    running = models.BooleanField(default=False, verbose_name="Running?", editable=False)
    _run = models.BooleanField(default=False, editable=False)
    _pause = models.BooleanField(default=False, editable=False)
    _restart = models.BooleanField(default=False, editable=False)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.slug)

    def build_kwargs(self):
        tracked_terms = self.tracked_terms.all()
        followed_users = self.followed_users.filter(user_id__isnull=False).exclude(user_id="")
        followed_locations = self.followed_locations.all()

        kwargs = {}

        if tracked_terms.count() > 0:
            kwargs['track'] = ",".join([term.phrase for term in tracked_terms if term.phrase is not None and term.phrase.strip() != ""])
        if followed_users.count() > 0:
            kwargs['follow'] = ",".join([user.user_id for user in followed_users if user.user_id is not None and user.user_id.strip() != ""])
        if followed_locations.count() > 0:
            kwargs['locations'] = ",".join([location.bounding_box for location in followed_locations if location.bounding_box is not None and location.bounding_box.strip() != ""])

        return kwargs

    def matches_criteria(self, tweet):
        """
        Twitter does an OR when you pass it params in the stream API.
        Thus any tweet matching a term OR a user OR a location will come through.

        This method makes sure that the given tweet matches any required criteria (specified by the required flag).
        """
        tracked_terms = self.tracked_terms.filter(required=True)
        followed_users = self.followed_users.filter(user_id__isnull=False, required=True).exclude(user_id="")
        followed_locations = self.followed_locations.filter(required=True)

        # check for tracked terms
        contains_required_terms = any([tweet.text.lower().find(term.phrase.lower()) != -1 for term in tracked_terms]) if tracked_terms.count() > 0 else True
        is_from_required_users = any([tweet.user.id == user.user_id for user in followed_users]) if followed_users.count() > 0 else True

        if followed_locations.count() > 0 and LOCATION_CALC_ENABLED:
            is_from_required_locations = False
            for location in followed_locations:
                bounding_box = location.bbox()
                pnt = tweet.get_coordinates()
                if pnt:
                    is_from_required_locations = pnt.within(bounding_box)
        else:
            is_from_required_locations = True

        return contains_required_terms and is_from_required_users and is_from_required_locations


class TrackedTerm(models.Model):
    stream = models.ForeignKey(Stream, related_name="tracked_terms")
    phrase = models.CharField(max_length=60)

    required = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{}'.format(self.phrase)


class FollowedUser(models.Model):
    stream = models.ForeignKey(Stream, related_name='followed_users')
    username = models.CharField(max_length=500)
    user_id = models.CharField(max_length=500, editable=False, null=True)

    required = models.BooleanField(default=False)

    def __unicode__(self):
        return u'@{}'.format(self.username)

    def save(self, *args, **kwargs):
        self.username = self.username.strip("@")

        # go out and get the user_id

        return super(FollowedUser, self).save(*args, **kwargs)


class FollowedLocation(models.Model):
    stream = models.ForeignKey(Stream, related_name='followed_locations')
    bounding_box = models.CharField(max_length=1000)

    required = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{}'.format(self.bounding_box)

    def bbox(self):
        return OGRGeometry(OGRGeometry.from_bbox(self.bounding_box.split(",")).json, srs=SpatialReference("WGS84"))


class JSONModel(models.Model):
    """
    Model that originates from JSON data
    """
    raw_data = JSONField(default={})

    class Meta:
        abstract = True


class TwitterUserManager(models.Manager):
    """
    Manages "TwitterUser" models
    """
    def create_user(self, user_obj):
        # do parsing of user obj to create new TwitterUser object
        data = parse_twitter_user_obj(user_obj)
        try:
            user = TwitterUser.objects.get(id=data['id'])
        except TwitterUser.DoesNotExist:
            user = TwitterUser()

        for key, val in data.items():
            setattr(user, key, val)

        user.save()
        return user


class TwitterUser(JSONModel):
    """
    Model representing a user on Twitter
    """
    id = models.CharField(max_length=255, primary_key=True)  # id_str

    name = models.CharField(max_length=255, default="")
    screen_name = models.CharField(max_length=100, default="")
    description = models.CharField(max_length=500, default="", null=True)
    profile_image_url = models.CharField(max_length=1000, default="")

    favourites_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)

    verified = models.BooleanField(default=False)

    objects = TwitterUserManager()

    def __unicode__(self):
        return u"@{}".format(self.screen_name)


class TweetManager(models.Manager):
    """
    Manages "Tweet" models
    """
    def create_tweet_for_stream(self, stream_or_slug, tweet_obj):
        stream = stream_or_slug
        if isinstance(stream, basestring):
            try:
                stream = Stream.objects.get(slug=stream_or_slug)
            except Stream.DoesNotExist:
                raise Exception("Cannot create tweet on a stream that doesn't exist.")

        # do parsing of tweet obj to create new Tweet object
        data = parse_tweet_obj(tweet_obj)
        data.update({
            'stream': stream
        })
        return self.create(**data)


class AbstractTweet(JSONModel):
    """
    Model representing a tweet on Twitter
    """
    id = models.CharField(max_length=255, primary_key=True)  # id_str

    in_reply_to_screen_name = models.CharField(max_length=255, default="", null=True)   # in_reply_to_screen_name
    in_reply_to_status_id = models.CharField(max_length=255, default="", null=True)     # in_reply_to_status_id_str
    in_reply_to_user_id = models.CharField(max_length=255, default="", null=True)       # in_reply_to_user_id_str

    place = JSONField(null=True)
    coordinates = JSONField(null=True)
    entities = JSONField(default={})

    retweet_count = models.IntegerField(default=0, null=True)
    favorite_count = models.IntegerField(default=0, null=True)

    text = models.CharField(max_length=400)

    user = models.ForeignKey(TwitterUser)

    stream = models.ForeignKey(Stream, related_name='tweets')

    created_at = models.DateTimeField()

    objects = TweetManager()

    class Meta:
        verbose_name = 'tweet'
        verbose_name_plural = 'tweets'
        abstract = True

    def __unicode__(self):
        return u"%s" % self.text

    def save(self, *args, **kwargs):
        # create user
        user = TwitterUser.objects.create_user(self.raw_data['user'])  # create a new twitter user from the raw user data
        self.user = user

        return super(AbstractTweet, self).save(*args, **kwargs)

    def get_coordinates(self):
        if self.coordinates and self.coordinates != {} and 'coordinates' in self.coordinates:
            pnt = OGRGeometry(json.dumps(self.coordinates), srs=SpatialReference("WGS84"))
            return pnt
        elif self.place and self.place != {} and "bounding_box" in self.place:
            bbox = self.place['bounding_box']
            for i, coordinate_chain in enumerate(bbox['coordinates']):
                coordinate_chain.append(coordinate_chain[0])
                bbox['coordinates'][i] = coordinate_chain
            polygon = OGRGeometry(json.dumps(bbox), srs=SpatialReference("WGS84"))
            return polygon.centroid
        else:
            return None

    def get_coordinates_tuple(self):
        coords = self.get_coordinates()
        if coords:
            return coords.tuple
        return None


class Tweet(AbstractTweet):

    class Meta(AbstractTweet.Meta):
        swappable = 'SOCIAL_STREAM_TWEET_MODEL'


@receiver(post_save, sender=get_tweet_model())
def post_tweet_save(sender, instance, created, *args, **kwargs):
    if not created:
        return

    if not instance.stream.matches_criteria(instance):
        instance.delete()
        return

    for pipeline in TWEET_PIPELINES:
        if callable(pipeline):
            result = pipeline().start(wait_for_result=False, instance=instance)
        else:
            result = PIPELINES.start(pipeline, wait_for_result=False, instance=instance)
