# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-30 03:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='文章标题')),
                ('categrory', models.CharField(max_length=20, verbose_name='文章分类')),
                ('limit', models.CharField(max_length=10, verbose_name='文章权限')),
                ('introduce', models.CharField(max_length=90, verbose_name='文章简介')),
                ('content', models.TextField(max_length=20, verbose_name='文章内容')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modifile_time', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserProfile')),
            ],
            options={
                'db_table': 'topic',
            },
        ),
    ]
