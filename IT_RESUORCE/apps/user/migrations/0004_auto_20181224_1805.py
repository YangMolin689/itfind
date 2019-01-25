# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-24 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20181223_1140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': '用户表', 'verbose_name_plural': '用户表'},
        ),
        migrations.RemoveField(
            model_name='user',
            name='image',
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status'),
        ),
    ]