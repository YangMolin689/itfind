# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-26 16:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('card', '0008_auto_20181226_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card_type',
            name='image',
        ),
    ]