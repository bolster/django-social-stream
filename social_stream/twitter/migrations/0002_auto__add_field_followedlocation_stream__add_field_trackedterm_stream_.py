# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FollowedLocation.stream'
        db.add_column(u'twitter_followedlocation', 'stream',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['twitter.Stream']),
                      keep_default=False)

        # Adding field 'TrackedTerm.stream'
        db.add_column(u'twitter_trackedterm', 'stream',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['twitter.Stream']),
                      keep_default=False)

        # Adding field 'FollowedUser.stream'
        db.add_column(u'twitter_followeduser', 'stream',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['twitter.Stream']),
                      keep_default=False)


        # Changing field 'FollowedUser.user_id'
        db.alter_column(u'twitter_followeduser', 'user_id', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))
        # Removing M2M table for field track on 'Stream'
        db.delete_table(db.shorten_name(u'twitter_stream_track'))

        # Removing M2M table for field locations on 'Stream'
        db.delete_table(db.shorten_name(u'twitter_stream_locations'))

        # Removing M2M table for field follow on 'Stream'
        db.delete_table(db.shorten_name(u'twitter_stream_follow'))


    def backwards(self, orm):
        # Deleting field 'FollowedLocation.stream'
        db.delete_column(u'twitter_followedlocation', 'stream_id')

        # Deleting field 'TrackedTerm.stream'
        db.delete_column(u'twitter_trackedterm', 'stream_id')

        # Deleting field 'FollowedUser.stream'
        db.delete_column(u'twitter_followeduser', 'stream_id')


        # Changing field 'FollowedUser.user_id'
        db.alter_column(u'twitter_followeduser', 'user_id', self.gf('django.db.models.fields.CharField')(default='', max_length=500))
        # Adding M2M table for field track on 'Stream'
        m2m_table_name = db.shorten_name(u'twitter_stream_track')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('stream', models.ForeignKey(orm[u'twitter.stream'], null=False)),
            ('trackedterm', models.ForeignKey(orm[u'twitter.trackedterm'], null=False))
        ))
        db.create_unique(m2m_table_name, ['stream_id', 'trackedterm_id'])

        # Adding M2M table for field locations on 'Stream'
        m2m_table_name = db.shorten_name(u'twitter_stream_locations')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('stream', models.ForeignKey(orm[u'twitter.stream'], null=False)),
            ('followedlocation', models.ForeignKey(orm[u'twitter.followedlocation'], null=False))
        ))
        db.create_unique(m2m_table_name, ['stream_id', 'followedlocation_id'])

        # Adding M2M table for field follow on 'Stream'
        m2m_table_name = db.shorten_name(u'twitter_stream_follow')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('stream', models.ForeignKey(orm[u'twitter.stream'], null=False)),
            ('followeduser', models.ForeignKey(orm[u'twitter.followeduser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['stream_id', 'followeduser_id'])


    models = {
        u'twitter.followedlocation': {
            'Meta': {'object_name': 'FollowedLocation'},
            'bounding_box': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter.Stream']"})
        },
        u'twitter.followeduser': {
            'Meta': {'object_name': 'FollowedUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter.Stream']"}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'twitter.stream': {
            'Meta': {'object_name': 'Stream'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"})
        },
        u'twitter.trackedterm': {
            'Meta': {'object_name': 'TrackedTerm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter.Stream']"})
        },
        u'twitter.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'coordinates': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'entities': ('jsonfield.fields.JSONField', [], {}),
            'favorite_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'in_reply_to_screen_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'in_reply_to_status_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'in_reply_to_user_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True'}),
            'place': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'possibly_sensitive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'raw_data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'retweet_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'stream': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter.Stream']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twitter.TwitterUser']"})
        },
        u'twitter.twitteruser': {
            'Meta': {'object_name': 'TwitterUser'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
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
