# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TwitterUser.description'
        db.alter_column(u'twitter_twitteruser', 'description', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

    def backwards(self, orm):

        # Changing field 'TwitterUser.description'
        db.alter_column(u'twitter_twitteruser', 'description', self.gf('django.db.models.fields.CharField')(max_length=500))

    models = {
        u'twitter.followedlocation': {
            'Meta': {'object_name': 'FollowedLocation'},
            'bounding_box': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'followed_locations'", 'to': u"orm['twitter.Stream']"})
        },
        u'twitter.followeduser': {
            'Meta': {'object_name': 'FollowedUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'followed_users'", 'to': u"orm['twitter.Stream']"}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'twitter.stream': {
            'Meta': {'object_name': 'Stream'},
            '_pause': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '_run': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"})
        },
        u'twitter.streamaccount': {
            'Meta': {'object_name': 'StreamAccount'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"})
        },
        u'twitter.trackedterm': {
            'Meta': {'object_name': 'TrackedTerm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tracked_terms'", 'to': u"orm['twitter.Stream']"})
        },
        u'twitter.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'coordinates': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'entities': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'favorite_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'in_reply_to_screen_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'in_reply_to_status_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'in_reply_to_user_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'place': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'raw_data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'retweet_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tweets'", 'to': u"orm['twitter.Stream']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter.TwitterUser']"})
        },
        u'twitter.twitteruser': {
            'Meta': {'object_name': 'TwitterUser'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'null': 'True'}),
            'favourites_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'followers_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'profile_image_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'raw_data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'screen_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['twitter']