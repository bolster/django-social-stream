from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from twython import Twython

from .models import *


### Stream Accounts ###

class StreamAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'default')
    fieldsets = (
        (None, {
            'fields': ('name', 'default')
        }),
        ("OAuth", {
            'fields': ('oauth_link', 'oauth_token', 'oauth_token_secret')
        })
    )
    readonly_fields = ('oauth_link', )

    def get_twitter_obj(self, request):
        key = getattr(settings, "TWITTER_ACCESS_TOKEN")
        secret = getattr(settings, "TWITTER_ACCESS_TOKEN_SECRET")
        oauth_token = request.session.get('oauth_token', None)
        oauth_token_secret = request.session.get('oauth_token_secret', None)
        if not oauth_token or not oauth_token_secret:
            twitter = Twython(key, secret)
        else:
            twitter = Twython(key, secret, oauth_token, oauth_token_secret)
        return twitter

    def do_oauth(self, request, extra_context):
        if request.GET.get('oauth_verifier', None) and request.session.get('oauth_token', None):
            twitter = self.get_twitter_obj(request)
            # do final verification
            final_step = twitter.get_authorized_tokens(request.GET.get('oauth_verifier'))
            request.session.update({
                'final_oauth_token': final_step['oauth_token'],
                'final_oauth_token_secret': final_step['oauth_token_secret']
            })

            return request, {"redirect": True}

        if 'oauth_token' in request.session:
            del request.session['oauth_token']
        if 'oauth_token_secret' in request.session:
            del request.session['oauth_token_secret']

        twitter = self.get_twitter_obj(request)
        auth = twitter.get_authentication_tokens(callback_url=request.build_absolute_uri())
        request.session['oauth_token'] = auth['oauth_token']
        request.session['oauth_token_secret'] = auth['oauth_token_secret']

        extra_context.update({
            'oauth_url': auth['auth_url']
        })
        if request.session.get('final_oauth_token'):
            extra_context.update({
                'oauth_token': request.session['final_oauth_token'],
                'oauth_token_secret': request.session['final_oauth_token_secret']
            })
            del request.session['final_oauth_token']
            del request.session['final_oauth_token_secret']
        return request, extra_context

    def add_view(self, request, form_url='', extra_context={}):
        request, extra_context = self.do_oauth(request, extra_context)
        if "redirect" in extra_context:
            return HttpResponseRedirect(request.META['PATH_INFO'])
        return super(StreamAccountAdmin, self).add_view(request, form_url='', extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context={}):
        request, extra_context = self.do_oauth(request, extra_context)
        if "redirect" in extra_context:
            return HttpResponseRedirect(request.META['PATH_INFO'])
        return super(StreamAccountAdmin, self).change_view(request, object_id, form_url='', extra_context=extra_context)

    def oauth_link(self, obj):
        return 'Authorize Account'
    oauth_link.allow_tags = True

admin.site.register(StreamAccount, StreamAccountAdmin)


### Streams ###


class TrackedTermInline(admin.TabularInline):
    model = TrackedTerm
    extra = 1


class FollowedUserInline(admin.TabularInline):
    model = FollowedUser
    extra = 1


class FollowedLocationInline(admin.TabularInline):
    model = FollowedLocation
    extra = 1


class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tracked_count', 'follow_count', 'location_count', 'tweet_count', 'running', '_run', '_pause')
    actions = ['start_stream', 'pause_stream']
    inlines = [
        TrackedTermInline,
        FollowedUserInline,
        FollowedLocationInline
    ]

    def tracked_count(self, obj):
        return obj.tracked_terms.count()
    tracked_count.short_description = "Tracked Terms"

    def follow_count(self, obj):
        return obj.followed_users.count()
    follow_count.short_description = "Followed Users"

    def location_count(self, obj):
        return obj.followed_locations.count()
    location_count.short_description = "Followed Locations"

    def tweet_count(self, obj):
        return obj.tweets.count()
    tweet_count.short_description = "Tweet Count"

    def start_stream(self, request, queryset):
        queryset.filter(running=False).update(_run=True, _pause=False)
    start_stream.short_description = "Start streams"

    def pause_stream(self, request, queryset):
        queryset.filter(running=True).update(_run=False, _pause=True)
    pause_stream.short_description = "Pause streams"


admin.site.register(Stream, StreamAdmin)


### Twitter Users ###


def twitter_user_screenname(obj):
    return u'@{}'.format(obj.screen_name)
twitter_user_screenname.short_description = "Screen Name"


def profile_image(obj):
    return '<img src="{}" alt="{}" width="30px" height="30px">'.format(obj.profile_image_url, obj.screen_name)
profile_image.allow_tags = True
profile_image.short_description = "Profile Image"


class TwitterUserAdmin(admin.ModelAdmin):
    list_display = (twitter_user_screenname, 'name', 'id', profile_image, )

    def has_add_permission(self, request):
        return False

admin.site.register(TwitterUser, TwitterUserAdmin)


### Tweets ###


class TweetAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'user', 'stream')

    def has_add_permission(self, request):
        return False

admin.site.register(Tweet, TweetAdmin)
