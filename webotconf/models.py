from django.db import models

# Create your models here.


class ChatRoom(models.Model):
    nickname = models.CharField(verbose_name='群名', max_length=50)
    order = models.IntegerField(verbose_name='优先级', unique=True)

    def __str__(self):
        return self.nickname


class RuleAddFriend(models.Model):
    keyword = models.CharField(verbose_name='关键字', max_length=20)
    chatroom = models.ForeignKey(ChatRoom, verbose_name='群', on_delete=models.CASCADE)

    def __str__(self):
        return self.keyword + '-' + self.chatroom.nickname


class QAKeyWord(models.Model):
    keyword = models.CharField(verbose_name='关键字', max_length=20)

    def __str__(self):
        return self.keyword


class QAReply(models.Model):
    disc = models.CharField(verbose_name='描述', max_length=30, blank=True, null=True)
    is_pic = models.BooleanField(verbose_name='是否图片', default=False)
    reply_text = models.TextField(verbose_name='回答', blank=True, null=True)
    reply_pic = models.ImageField(verbose_name='图片回答', blank=True, null=True)
    keywords = models.ManyToManyField(QAKeyWord, verbose_name='关键字集', related_name='replies')

    def __str__(self):
        return self.disc
