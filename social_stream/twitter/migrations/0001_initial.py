# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrackedTerm'
        db.create_table(u'twitter_trackedterm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal(u'twitter', ['TrackedTerm'])

        # Adding model 'FollowedUser'
        db.create_table(u'twitter_followeduser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'twitter', ['FollowedUser'])

        # Adding model 'FollowedLocation'
        db.create_table(u'twitter_followedlocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bounding_box', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal(u'twitter', ['FollowedLocation'])

        # Adding model 'Stream'
        db.create_table(u'twitter_stream', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name')),
        ))
        db.send_create_signal(u'twitter', ['Stream'])

        # Adding M2M table for field follow on 'Stream'
        m2m_table_name = db.shorten_name(u'twitter_stream_follow')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('stream', models.ForeignKey(orm[u'twitter.stream'], null=False)),
            ('followeduser', models.ForeignKey(orm[u'twitter.followeduser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['stream_id', 'followeduser_id'])

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

        # Adding model 'TwitterUser'
        db.create_table(u'twitter_twitteruser', (
            ('raw_data', self.gf('jsonfield.fields.JSONField')()),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('screen_name', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=500)),
            ('profile_image_url', self.gf('django.db.models.fields.CharField')(default='', max_length=1000)),
            ('favourites_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('followers_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('friends_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'twitter', ['TwitterUser'])

        # Adding model 'Tweet'
        db.create_table(u'twitter_tweet', (
            ('raw_data', self.gf('jsonfield.fields.JSONField')()),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('in_reply_to_screen_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True)),
            ('in_reply_to_status_id', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True)),
            ('in_reply_to_user_id', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True)),
            ('place', self.gf('jsonfield.fields.JSONField')(null=True)),
            ('coordinates', self.gf('jsonfield.fields.JSONField')(null=True)),
            ('entities', self.gf('jsonfield.fields.JSONField')()),
            ('possibly_sensitive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('retweet_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('favorite_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['twitter.TwitterUser'])),
            ('stream', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['twitter.Stream'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'twitter', ['Tweet'])


    def backwards(self, orm):
        # Deleting model 'TrackedTerm'
        db.delete_table(u'twitter_trackedterm')

        # Deleting model 'FollowedUser'
        db.delete_table(u'twitter_followeduser')

        # Deleting model 'FollowedLocation'
        db.delete_table(u'twitter_followedlocation')

        # Deleting model 'Stream'
        db.delete_table(u'twitter_stream')

        # Removing M2M table for field follow on 'Stream'
        db.delete_table(db.shorten_name(u'twitter_stream_follow'))

        # Removing M2M table for field track on 'Stream'
        db.delete_table(db.shorten_name(u'twitter_stream_track'))

        # Removing M2M table for field locations on 'Stream'
        db.delete_table(db.shorten_name(u'twitter_stream_locations'))

        # Deleting model 'TwitterUser'
        db.delete_table(u'twitter_twitteruser')

        # Deleting model 'Tweet'
        db.delete_table(u'twitter_tweet')


    models = {
        u'twitter.followedlocation': {
            'Meta': {'object_name': 'FollowedLocation'},
            'bounding_box': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'twitter.followeduser': {
            'Meta': {'object_name': 'FollowedUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'twitter.stream': {
            'Meta': {'object_name': 'Stream'},
            'follow': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['twitter.FollowedUser']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['twitter.FollowedLocation']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"}),
            'track': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['twitter.TrackedTerm']", 'null': 'True', 'blank': 'True'})
        },
        u'twitter.trackedterm': {
            'Meta': {'object_name': 'TrackedTerm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '60'})
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
            'raw_data': ('jsonfield.fields.JSONField', [], {}),
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
            'raw_data': ('jsonfield.fields.JSONField', [], {}),
            'screen_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['twitter']