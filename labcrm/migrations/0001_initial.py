# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 13:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttrOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(max_length=255, verbose_name='选项')),
            ],
        ),
        migrations.CreateModel(
            name='LabUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=30, verbose_name='昵称')),
                ('wechat', models.CharField(max_length=30, verbose_name='微信号')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='labuser', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='建表时间')),
                ('finished_time', models.DateTimeField(null=True, verbose_name='填写时间')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='papers', to='labcrm.LabUser', verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='UserAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr', models.CharField(max_length=255, verbose_name='属性')),
                ('is_option', models.BooleanField(default=False, verbose_name='是否提供选项')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfoA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=255, verbose_name='回答')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfoQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('attr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='labcrm.UserAttr', verbose_name='属性')),
                ('paper', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='labcrm.Paper', verbose_name='问卷')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='labcrm.LabUser', verbose_name='用户')),
            ],
        ),
        migrations.AddField(
            model_name='userinfoa',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='labcrm.UserInfoQ', verbose_name='问题'),
        ),
        migrations.AddField(
            model_name='userinfoa',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='labcrm.LabUser', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='attroption',
            name='attr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='labcrm.UserAttr', verbose_name='属性'),
        ),
    ]
