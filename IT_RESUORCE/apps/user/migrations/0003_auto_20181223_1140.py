# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-23 03:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20181222_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default=True, upload_to='head', verbose_name='头像'),
        ),
    ]
