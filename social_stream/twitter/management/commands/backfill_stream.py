import re
import sys
import time
import threading

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
from twython import Twython

from social_stream.twitter.models import *

from social_stream.twitter import get_tweet_model


class Command(BaseCommand):
    help = 'Starts tweet streamer'

    option_list = BaseCommand.option_list + (
        make_option('--stream',
                    action='store',
                    dest='stream_slug',
                    default="",
                    help='Slug of stream to start.'),
        make_option('--account',
                    action='store',
                    dest="account_slug",
                    default="",
                    help="Slug of account to use for stream."),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__()

    def search(self, max_id=None):
        twitter = Twython(self.key, self.secret, self.token, self.token_secret)
        kwargs = {
            'q': self.stream.build_search_query(),
            'count': 100,
            'result_type': "recent",
        }
        if max_id:
            kwargs['max_id'] = max_id

        print kwargs
        tweets = twitter.search(**kwargs)

        if 'next_results' in tweets['search_metadata'] and tweets['search_metadata']['next_results'] != "":
            max_id = re.search(r'\?max_id\=(\d+)', tweets['search_metadata']['next_results']).groups()[0]
            more = self.search(max_id=max_id)
            if 'statuses' in more and more['statuses'] is not None and len(more['statuses']) > 0:
                statuses = tweets['statuses']
                statuses.extend(more['statuses'])
                tweets['statuses'] = statuses
                return tweets
            return tweets
        return tweets

    def handle(self, *args, **options):
        if not options['stream_slug']:
            raise CommandError("Stream name is required.")

        try:
            self.stream = Stream.objects.get(slug=options['stream_slug'])
        except Stream.DoesNotExist:
            raise CommandError("Specified stream cannot be found.")

        # AUTHENTICATE
        self.key = getattr(settings, "TWITTER_ACCESS_TOKEN")
        self.secret = getattr(settings, "TWITTER_ACCESS_TOKEN_SECRET")

        try:
            stream_account = StreamAccount.objects.get(slug=options['account_slug'])
        except StreamAccount.DoesNotExist:
            self.stdout.write("Stream account specified does not exist. Using default acccount...")
            stream_account = StreamAccount.objects.get_default_account()

        if not stream_account:
            raise CommandError("Please setup a stream account.")

        self.token, self.token_secret = stream_account.auth_data()
        # END AUTHENTICATE

        try:
            tweets = self.search()
            # for status in tweets['statuses']:
            for tweet in tweets['statuses']:
                print tweet
                get_tweet_model().objects.create_tweet_for_stream(self.stream, tweet)

        except KeyboardInterrupt:
            time.sleep(1)
            self.stdout.write("\n\nStopping backfill.")
            sys.exit(0)
