# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        if db.backend_name == 'postgres':
            db.execute("ALTER TABLE thing_apikey DROP CONSTRAINT thing_apikey_pkey")
            db.execute("ALTER TABLE thing_apikey RENAME COLUMN id TO keyid")
            db.execute("ALTER TABLE thing_apikey ADD COLUMN id INTEGER NOT NULL PRIMARY KEY")
            db.execute("CREATE SEQUENCE thing_apikey_id_seq")
            db.execute("SELECT setval('thing_apikey_id_seq', 1)")
            db.execute("ALTER TABLE thing_apikey ALTER COLUMN id SET DEFAULT nextval('thing_apikey_id_seq'::regclass)")
        elif db.backend_name == 'mysql':
            db.delete_primary_key('thing_apikey')
            db.rename_column('thing_apikey', 'id', 'keyid')
            db.add_column('thing_apikey', 'id', models.AutoField(primary_key=True))
        # try a fallback for any other weird databases
        else:
            db.delete_primary_key('thing_apikey')
            db.rename_column('thing_apikey', 'id', 'keyid')
            db.add_column('thing_apikey', 'id', models.AutoField(primary_key=True, default=0), keep_default=False)

    def backwards(self, orm):
        db.delete_primary_key('thing_apikey')
        db.delete_column('thing_apikey', 'id')
        db.rename_column('thing_apikey', 'keyid', 'id')
        db.create_primary_key('thing_apikey', 'id')

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
        'thing.apicache': {
            'Meta': {'object_name': 'APICache'},
            'cached_until': ('django.db.models.fields.DateTimeField', [], {}),
            'completed_ok': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'error_displayed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'thing.apikey': {
            'Meta': {'ordering': "('keyid',)", 'object_name': 'APIKey'},
            'access_mask': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'corp_character': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'corporate_apikey'", 'null': 'True', 'to': "orm['thing.Character']"}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'key_type': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'keyid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'paid_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'vcode': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.asset': {
            'Meta': {'object_name': 'Asset'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']", 'null': 'True', 'blank': 'True'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Corporation']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'inv_flag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.InventoryFlag']"}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Item']"}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['thing.Asset']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'raw_quantity': ('django.db.models.fields.IntegerField', [], {}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'singleton': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Station']", 'null': 'True', 'blank': 'True'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.System']", 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'thing.blueprint': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Blueprint'},
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'component_of'", 'symmetrical': 'False', 'through': "orm['thing.BlueprintComponent']", 'to': "orm['thing.Item']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Item']"}),
            'material_modifier': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'production_time': ('django.db.models.fields.IntegerField', [], {}),
            'productivity_modifier': ('django.db.models.fields.IntegerField', [], {}),
            'waste_factor': ('django.db.models.fields.IntegerField', [], {})
        },
        'thing.blueprintcomponent': {
            'Meta': {'object_name': 'BlueprintComponent'},
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Blueprint']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Item']"}),
            'needs_waste': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'thing.blueprintinstance': {
            'Meta': {'ordering': "('blueprint',)", 'object_name': 'BlueprintInstance'},
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Blueprint']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'material_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'original': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'productivity_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'thing.campaign': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Campaign'},
            'characters': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['thing.Character']", 'null': 'True', 'blank': 'True'}),
            'corp_wallets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['thing.CorpWallet']", 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'thing.character': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Character'},
            'brokers_fee': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'max_digits': '3', 'decimal_places': '2'}),
            'cha_attribute': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'cha_bonus': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'clone_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'clone_skill_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Corporation']"}),
            'corporation_standings': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'has_standings'", 'symmetrical': 'False', 'through': "orm['thing.CorporationStanding']", 'to': "orm['thing.Corporation']"}),
            'faction_standings': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'has_standings'", 'symmetrical': 'False', 'through': "orm['thing.FactionStanding']", 'to': "orm['thing.Faction']"}),
            'factory_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'factory_per_hour': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'int_attribute': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'int_bonus': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'mem_attribute': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'mem_bonus': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'per_attribute': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'per_bonus': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'sales_tax': ('django.db.models.fields.DecimalField', [], {'default': '1.5', 'max_digits': '3', 'decimal_places': '2'}),
            'skill_queue': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'training_by'", 'symmetrical': 'False', 'through': "orm['thing.SkillQueue']", 'to': "orm['thing.Skill']"}),
            'skills': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'learned_by'", 'symmetrical': 'False', 'through': "orm['thing.CharacterSkill']", 'to': "orm['thing.Skill']"}),
            'wallet_balance': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '18', 'decimal_places': '2'}),
            'wil_attribute': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'wil_bonus': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'thing.characterconfig': {
            'Meta': {'object_name': 'CharacterConfig'},
            'anon_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'character': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'config'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['thing.Character']"}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_clone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_implants': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_skill_queue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_standings': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_wallet': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'thing.characterskill': {
            'Meta': {'object_name': 'CharacterSkill'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.SmallIntegerField', [], {}),
            'points': ('django.db.models.fields.IntegerField', [], {}),
            'skill': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Skill']"})
        },
        'thing.constellation': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Constellation'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Region']"})
        },
        'thing.corporation': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Corporation'},
            'division1': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'division2': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'division3': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'division4': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'division5': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'division6': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'division7': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ticker': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'thing.corporationstanding': {
            'Meta': {'ordering': "('-standing',)", 'object_name': 'CorporationStanding'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']"}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Corporation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'standing': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'})
        },
        'thing.corpwallet': {
            'Meta': {'ordering': "('corporation', 'account_id')", 'object_name': 'CorpWallet'},
            'account_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'account_key': ('django.db.models.fields.IntegerField', [], {}),
            'balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '2'}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Corporation']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.event': {
            'Meta': {'ordering': "('-issued', '-id')", 'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued': ('django.db.models.fields.DateTimeField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'thing.faction': {
            'Meta': {'object_name': 'Faction'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.factionstanding': {
            'Meta': {'ordering': "('-standing',)", 'object_name': 'FactionStanding'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']"}),
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Faction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'standing': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'})
        },
        'thing.inventoryflag': {
            'Meta': {'object_name': 'InventoryFlag'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'thing.item': {
            'Meta': {'object_name': 'Item'},
            'buy_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'item_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.ItemGroup']"}),
            'market_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.MarketGroup']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'portion_size': ('django.db.models.fields.IntegerField', [], {}),
            'sell_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2'}),
            'volume': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '4'})
        },
        'thing.itemcategory': {
            'Meta': {'object_name': 'ItemCategory'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.itemgroup': {
            'Meta': {'object_name': 'ItemGroup'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.ItemCategory']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.marketgroup': {
            'Meta': {'object_name': 'MarketGroup'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['thing.MarketGroup']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'thing.marketorder': {
            'Meta': {'ordering': "('buy_order', 'item__name')", 'object_name': 'MarketOrder'},
            'buy_order': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']"}),
            'corp_wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.CorpWallet']", 'null': 'True', 'blank': 'True'}),
            'escrow': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'issued': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Item']"}),
            'minimum_volume': ('django.db.models.fields.IntegerField', [], {}),
            'order_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Station']"}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '17', 'decimal_places': '2'}),
            'volume_entered': ('django.db.models.fields.IntegerField', [], {}),
            'volume_remaining': ('django.db.models.fields.IntegerField', [], {})
        },
        'thing.pricehistory': {
            'Meta': {'ordering': "('-date',)", 'unique_together': "(('region', 'item', 'date'),)", 'object_name': 'PriceHistory'},
            'average': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Item']"}),
            'maximum': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '2'}),
            'minimum': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '2'}),
            'movement': ('django.db.models.fields.BigIntegerField', [], {}),
            'orders': ('django.db.models.fields.IntegerField', [], {}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Region']"})
        },
        'thing.reftype': {
            'Meta': {'object_name': 'RefType'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.region': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Region'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'thing.skill': {
            'Meta': {'object_name': 'Skill'},
            'item': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['thing.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'primary_attribute': ('django.db.models.fields.SmallIntegerField', [], {}),
            'rank': ('django.db.models.fields.SmallIntegerField', [], {}),
            'secondary_attribute': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'thing.skillqueue': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'SkillQueue'},
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']"}),
            'end_sp': ('django.db.models.fields.IntegerField', [], {}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'skill': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Skill']"}),
            'start_sp': ('django.db.models.fields.IntegerField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'to_level': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'thing.station': {
            'Meta': {'object_name': 'Station'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.System']"})
        },
        'thing.system': {
            'Meta': {'ordering': "('name',)", 'object_name': 'System'},
            'constellation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Constellation']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'thing.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'buy_transaction': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'character': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Character']"}),
            'corp_wallet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.CorpWallet']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Item']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['thing.Station']"}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '17', 'decimal_places': '2'}),
            'transaction_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'thing.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'home_chars_per_row': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'home_sort_descending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'home_sort_order': ('django.db.models.fields.CharField', [], {'default': "'apiname'", 'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'theme-default'", 'max_length': '32'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['thing']
