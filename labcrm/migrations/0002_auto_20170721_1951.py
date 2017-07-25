# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-21 11:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labcrm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dialog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dialog', models.TextField(verbose_name='对话记录')),
                ('log_time', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('recorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='记录员')),
            ],
        ),
        migrations.CreateModel(
            name='PicData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic', models.ImageField(unique=True, upload_to='img/gallery', verbose_name='地址')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('name', models.CharField(max_length=30, verbose_name='图片名')),
            ],
        ),
        migrations.CreateModel(
            name='UserPic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic_type', models.CharField(default='未分类', max_length=30, verbose_name='图片类型')),
                ('upic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upic', to='labcrm.PicData', verbose_name='图片')),
            ],
        ),
        migrations.AddField(
            model_name='labuser',
            name='class_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='教室ID'),
        ),
        migrations.AddField(
            model_name='labuser',
            name='is_del',
            field=models.BooleanField(default=False, verbose_name='是否删除'),
        ),
        migrations.AddField(
            model_name='paper',
            name='data',
            field=models.TextField(default=1, verbose_name='问卷数据'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paper',
            name='is_fill',
            field=models.BooleanField(default=False, verbose_name='是否填写'),
        ),
        migrations.AddField(
            model_name='paper',
            name='key',
            field=models.IntegerField(default=1, verbose_name='秘钥'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paper',
            name='finished_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='填写时间'),
        ),
        migrations.AddField(
            model_name='userpic',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upic', to='labcrm.LabUser', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='dialog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labcrm.LabUser', verbose_name='用户'),
        ),
    ]