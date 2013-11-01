import sys
import time
import threading

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
from twython import TwythonStreamer

from social_stream.twitter.models import *


class Streamer(TwythonStreamer):

    def __init__(self, *args, **kwargs):
        if "stream" in kwargs:
            self.stream = kwargs.pop("stream")
        super(Streamer, self).__init__(*args, **kwargs)

    def on_success(self, data):
        if 'text' in data:
            Tweet.objects.create_tweet_for_stream(self.stream, data)

    def on_error(self, status_code, data):
        # print status_code

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        # self.disconnect()
        pass


class StreamerThread(threading.Thread):

    def __init__(self, key, secret, oauth_token, oauth_token_secret, stream):
        super(StreamerThread, self).__init__()
        self.key = key
        self.secret = secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.stream = stream
        self.shutdown = False

    def run(self):
        self.streamer = Streamer(self.key, self.secret, self.oauth_token, self.oauth_token_secret, stream=self.stream)
        self.streamer.statuses.filter(**self.stream.build_kwargs())

    def stop(self):
        self.streamer.disconnect()
        self.streamer = None


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
        self.stream_thread = None

    def start_stream_thread(self):
        if self.stream_thread:
            return

        self.stdout.write("\nStarting stream.\n\n")

        self.stream_thread = StreamerThread(self.key, self.secret, self.token, self.token_secret, self.stream)
        self.stream_thread.start()

        self.stream._run = False
        self.stream._pause = False
        self.stream.running = True
        self.stream.save()

    def stop_stream_thread(self):
        if not self.stream_thread:
            return

        self.stdout.write("\nPausing stream.\n\n")

        self.stream_thread.stop()
        self.stream_thread.join()
        self.stream_thread = None

        self.stream._run = False
        self.stream._pause = False
        self.stream.running = False
        self.stream.save()

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

        if self.stream.running or self.stream._run:
            self.start_stream_thread()

        try:

            while True:
                self.stdout.write("Checking stream status...")
                self.stream = Stream.objects.get(pk=self.stream.pk)
                if self.stream._run and not self.stream.running:
                    # start stream thread
                    self.start_stream_thread()
                elif self.stream._pause and self.stream.running:
                    # stop stream thread
                    self.stop_stream_thread()

                time.sleep(5)
        except KeyboardInterrupt:
            self.stop_stream_thread()
            time.sleep(1)
            self.stdout.write("\n\nStopping stream monitor.")
            sys.exit(0)
