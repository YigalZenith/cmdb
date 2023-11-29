#coding: utf-8
from django.db import models

class result(models.Model):
    fun = models.CharField(max_length=50)
    jid = models.CharField(max_length=255)
    result = models.TextField()
    host = models.CharField(max_length=255)
    success = models.CharField(max_length=10)
    full_ret = models.TextField()

    def __unicode__(self):
        return self.host

    class Meta:
        verbose_name = u'命令返回结果'
        verbose_name_plural = u'命令返回结果'


