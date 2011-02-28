# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Image'
        db.create_table('massmedia_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('one_off_author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('metadata', self.gf('massmedia.fields.SerializedObjectField')(blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='image_site', to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('widget_template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('thumb_width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('thumb_height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('original', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='variations', null=True, to=orm['massmedia.Image'])),
        ))
        db.send_create_signal('massmedia', ['Image'])

        # Adding model 'Embed'
        db.create_table('massmedia_embed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('one_off_author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('metadata', self.gf('massmedia.fields.SerializedObjectField')(blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='embed_site', to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('widget_template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('massmedia', ['Embed'])

        # Adding model 'Video'
        db.create_table('massmedia_video', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('one_off_author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('metadata', self.gf('massmedia.fields.SerializedObjectField')(blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='video_site', to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('widget_template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['massmedia.Image'], null=True, blank=True)),
        ))
        db.send_create_signal('massmedia', ['Video'])

        # Adding model 'GrabVideo'
        db.create_table('massmedia_grabvideo', (
            ('video_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['massmedia.Video'], unique=True, primary_key=True)),
            ('asset_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('layout_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keywords', self.gf('tagging.fields.TagField')(null=True)),
        ))
        db.send_create_signal('massmedia', ['GrabVideo'])

        # Adding model 'Audio'
        db.create_table('massmedia_audio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('one_off_author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('metadata', self.gf('massmedia.fields.SerializedObjectField')(blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='audio_site', to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('widget_template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('massmedia', ['Audio'])

        # Adding model 'Flash'
        db.create_table('massmedia_flash', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('one_off_author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('metadata', self.gf('massmedia.fields.SerializedObjectField')(blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='flash_site', to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('widget_template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('massmedia', ['Flash'])

        # Adding model 'Document'
        db.create_table('massmedia_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('one_off_author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('metadata', self.gf('massmedia.fields.SerializedObjectField')(blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='document_site', to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
            ('reproduction_allowed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('external_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('widget_template', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('massmedia', ['Document'])

        # Adding model 'Collection'
        db.create_table('massmedia_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('zip_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('categories', self.gf('tagging.fields.TagField')(null=True)),
        ))
        db.send_create_signal('massmedia', ['Collection'])

        # Adding model 'CollectionRelation'
        db.create_table('massmedia_collectionrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['massmedia.Collection'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('massmedia', ['CollectionRelation'])

        # Adding model 'MediaTemplate'
        db.create_table('massmedia_mediatemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('massmedia', ['MediaTemplate'])


    def backwards(self, orm):
        
        # Deleting model 'Image'
        db.delete_table('massmedia_image')

        # Deleting model 'Embed'
        db.delete_table('massmedia_embed')

        # Deleting model 'Video'
        db.delete_table('massmedia_video')

        # Deleting model 'GrabVideo'
        db.delete_table('massmedia_grabvideo')

        # Deleting model 'Audio'
        db.delete_table('massmedia_audio')

        # Deleting model 'Flash'
        db.delete_table('massmedia_flash')

        # Deleting model 'Document'
        db.delete_table('massmedia_document')

        # Deleting model 'Collection'
        db.delete_table('massmedia_collection')

        # Deleting model 'CollectionRelation'
        db.delete_table('massmedia_collectionrelation')

        # Deleting model 'MediaTemplate'
        db.delete_table('massmedia_mediatemplate')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'massmedia.audio': {
            'Meta': {'object_name': 'Audio'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('massmedia.fields.SerializedObjectField', [], {'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'one_off_author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'audio_site'", 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'widget_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'massmedia.collection': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Collection'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zip_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'massmedia.collectionrelation': {
            'Meta': {'object_name': 'CollectionRelation'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['massmedia.Collection']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'massmedia.document': {
            'Meta': {'object_name': 'Document'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('massmedia.fields.SerializedObjectField', [], {'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'one_off_author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'document_site'", 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'widget_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'massmedia.embed': {
            'Meta': {'ordering': "('-creation_date',)", 'object_name': 'Embed'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('massmedia.fields.SerializedObjectField', [], {'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'one_off_author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'embed_site'", 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'widget_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'massmedia.flash': {
            'Meta': {'object_name': 'Flash'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('massmedia.fields.SerializedObjectField', [], {'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'one_off_author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flash_site'", 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'widget_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'massmedia.grabvideo': {
            'Meta': {'ordering': "('-creation_date',)", 'object_name': 'GrabVideo', '_ormbases': ['massmedia.Video']},
            'asset_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'keywords': ('tagging.fields.TagField', [], {'null': 'True'}),
            'layout_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['massmedia.Video']", 'unique': 'True', 'primary_key': 'True'})
        },
        'massmedia.image': {
            'Meta': {'ordering': "('-creation_date',)", 'object_name': 'Image'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('massmedia.fields.SerializedObjectField', [], {'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'one_off_author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'original': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variations'", 'null': 'True', 'to': "orm['massmedia.Image']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'image_site'", 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'thumb_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumb_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'widget_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'massmedia.mediatemplate': {
            'Meta': {'object_name': 'MediaTemplate'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'massmedia.video': {
            'Meta': {'ordering': "('-creation_date',)", 'object_name': 'Video'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'categories': ('tagging.fields.TagField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('massmedia.fields.SerializedObjectField', [], {'blank': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'one_off_author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reproduction_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'video_site'", 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['massmedia.Image']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'widget_template': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['massmedia']
