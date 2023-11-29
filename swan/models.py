# coding: utf-8
from django.db import models
from uuidfield import UUIDField


class OnlineRecordLog(models.Model):
    username = models.CharField(max_length=50, verbose_name=u'操作人员')
    optime = models.DateTimeField(auto_now=True, verbose_name=u'操作时间')
    action = models.CharField(max_length=150, verbose_name=u'操作命令')
    URL = models.URLField(blank=False, verbose_name="网址")
    MD5 = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'MD5值')

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = u"项目记录日志"
        verbose_name_plural = verbose_name
        app_label = 'swan'


class OnlineLog(models.Model):
    username = models.CharField(max_length=50, verbose_name=u'操作人员')
    optime = models.DateTimeField(auto_now=True, verbose_name=u'操作时间')
    action = models.CharField(blank=True, null=True, max_length=100, verbose_name=u'操作内容')
    command = models.CharField(max_length=150, verbose_name=u'操作命令')
    # 1--上线，2--执行命令, 3---查看日志
    tag = models.SmallIntegerField(verbose_name=u'操作类型')
    pname = models.CharField(max_length=60, blank=True, null=True, verbose_name=u'项目名')
    hid = UUIDField()
    hname = models.CharField(max_length=100, blank=True, null=True, verbose_name=u"主机名")
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.hname

    class Meta:
        verbose_name = u"项目上线日志"
        verbose_name_plural = verbose_name
        app_label = 'swan'
