# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-01-24 11:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20181225_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to='type', verbose_name='头像路径'),
        ),
    ]