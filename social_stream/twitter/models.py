import datetime

from django.db import models
from jsonfield import JSONField

from autoslug.fields import AutoSlugField


__ALL__ = ["Tweet", "TwitterUser", "StreamAccount", "Stream", "TrackedTerm", "FollowedUser", "FollowedLocation"]


def parse_twitter_date(date_str):
    return datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y')


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
        'text': tweet_obj['text'].encode('utf-8'),
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


class TrackedTerm(models.Model):
    stream = models.ForeignKey(Stream, related_name="tracked_terms")
    phrase = models.CharField(max_length=60)

    def __unicode__(self):
        return u'{}'.format(self.phrase)


class FollowedUser(models.Model):
    stream = models.ForeignKey(Stream, related_name='followed_users')
    username = models.CharField(max_length=500)
    user_id = models.CharField(max_length=500, editable=False, null=True)

    def __unicode__(self):
        return u'@{}'.format(self.username)

    def save(self, *args, **kwargs):
        self.username = self.username.strip("@")

        # go out and get the user_id

        return super(FollowedUser, self).save(*args, **kwargs)


class FollowedLocation(models.Model):
    stream = models.ForeignKey(Stream, related_name='followed_locations')
    bounding_box = models.CharField(max_length=1000)

    def __unicode__(self):
        return u'{}'.format(self.bounding_box)


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


class Tweet(JSONModel):
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

    def __unicode__(self):
        return u"{}".format(self.text)

    def save(self, *args, **kwargs):
        # create user
        user = TwitterUser.objects.create_user(self.raw_data['user'])  # create a new twitter user from the raw user data
        self.user = user

        return super(Tweet, self).save(*args, **kwargs)