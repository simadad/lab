from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class LabUser(models.Model):
    user = models.OneToOneField(User, verbose_name='用户', on_delete=models.CASCADE, related_name='labuser')
    nickname = models.CharField(max_length=30, verbose_name='昵称')
    wechat = models.CharField(max_length=30, verbose_name='微信号')

    def __str__(self):
        return self.nickname


class Paper(models.Model):
    user = models.ForeignKey(LabUser, verbose_name='用户', related_name='papers')
    create_time = models.DateTimeField(verbose_name='建表时间', auto_now_add=True)
    finished_time = models.DateTimeField(verbose_name='填写时间', null=True)
    is_fill = models.BooleanField(verbose_name='是否填写', default=False)
    is_del = models.BooleanField(verbose_name='是否删除', default=False)

    def __str__(self):
        name = self.user.nickname + ' ' + self.create_time.strftime('%Y-%m-%d')
        return name


class PaPerData(models.Model):
    paper = models.ForeignKey(Paper, verbose_name='问卷', related_name='datas')
    key = models.CharField(verbose_name='秘钥', max_length=255)
    data = models.TextField(verbose_name='问卷页面')

    def __str__(self):
        name = 'html' + self.paper.user.nickname + ' ' + self.create_time.strftime('%Y-%m-%d')
        return name


class UserAttr(models.Model):
    attr = models.CharField(verbose_name='属性', max_length=255)
    is_option = models.BooleanField(verbose_name='是否提供选项', default=False)

    def __str__(self):
        return self.attr


class Dialog(models.Model):
    dialog = models.TextField(verbose_name='对话记录')
    user = models.ForeignKey(LabUser, verbose_name='用户')
    recorder = models.ForeignKey(User, verbose_name='记录员')
    log_time = models.DateTimeField(verbose_name='记录时间', auto_now_add=True)

    def __str__(self):
        name = self.user.nickname + ' ' + self.log_time.strftime('%Y-%m-%d')
        return name


class AttrOption(models.Model):
    option = models.CharField(verbose_name='选项', max_length=255)
    attr = models.ForeignKey(UserAttr, verbose_name='属性', related_name='options')

    def __str__(self):
        return self.option


class UserInfoQ(models.Model):
    user = models.ForeignKey(LabUser, verbose_name='用户', related_name='questions')
    paper = models.ForeignKey(Paper, verbose_name='问卷', related_name='questions', blank=True, null=True)
    attr = models.ForeignKey(UserAttr, verbose_name='属性', related_name='questions')
    is_del = models.BooleanField(verbose_name='是否删除', default=False)

    def __str__(self):
        return self.attr.attr


class UserInfoA(models.Model):
    user = models.ForeignKey(LabUser, verbose_name='用户', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(UserInfoQ, verbose_name='问题', on_delete=models.CASCADE, related_name='answers')
    answer = models.CharField(verbose_name='回答', max_length=255)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    is_del = models.BooleanField(verbose_name='是否删除', default=False)

    def __str__(self):
        return self.answer

# GENDER_CHOICES = (
#     ('S', '保密'),
#     ('M', '男'),
#     ('F', '女'),
# )
# AGE_CHOICES = (
#     ('S', '保密'),  # Secret
#     ('C', '童年'),  # Childhood
#     ('J', '少年'),  # Juvenile
#     ('P', '青年'),  # Puberty
#     ('P', '壮年'),  # Prime of life
#     ('M', '中年'),  # Middle-aged
#     ('O', '老年'),  # Old Age
# )
# age = models.CharField(max_length=2, default='S', choices=AGE_CHOICES)
# gender = models.CharField(max_length=2, default='S', choices=GENDER_CHOICES)
# etc = models.TextField()
