#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from uuidfield import UUIDField
import time


idc_type = (
    (0, u"CDN"),
    (1, u"核心")
)

idc_operator = (
    (0, u"电信"),
    (1, u"联通"),
    (2, u"BGP"),
)


class IDC(models.Model):
    uuid = UUIDField(auto=True, primary_key=True)
    name = models.CharField(max_length=64, verbose_name=u'机房名称')
    bandwidth = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'机房带宽')
    phone = models.CharField(max_length=32, verbose_name=u'联系电话')
    linkman = models.CharField(max_length=32, null=True, verbose_name=u'联系人')
    address = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"机房地址")
    network = models.TextField(blank=True, null=True, verbose_name=u"IP地址段")
    create_time = models.DateField(auto_now=True)
    operator = models.IntegerField(verbose_name=u"运营商", choices=idc_operator, max_length=32, blank=True, null=True)
    type = models.IntegerField(verbose_name=u"机房类型", choices=idc_type, max_length=32, blank=True, null=True)
    comment = models.TextField(blank=True, null=True, verbose_name=u"备注")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"IDC机房"
        verbose_name_plural = verbose_name
        app_label = 'assets'


VENDORS = (
        (1,"惠普"),
        (2,"戴尔"),
    )

DEVICE_TYPES = (
        (1,"服务器"),
        (2,"防火墙"),
        (3,"交换机"),
        (4,"存储"),
    )

MODELS = [
    (i, i) for i in
    (
        u"Dell R410",
        u"Dell R420",
        u"Dell R610",
        u"Dell R620",
        u"Dell R710",
        u"Dell R720",
        u"Dell R730",
        u"Dell R720xd",
        u"Dell R730xd",
        u"HP DL360p",
        u"HP DL380e",
        u"HP DL160",
        u"Lenovo",
        u"Lenovo WQ R510 G7",
        u"Lenovo ThinkServer RD330",
        u"Lenovo ThinkServer RD340",
        u"DIY",
        u"VIP",
        u"虚拟化",
        u"Other",
        u"MediaServer",
        u"网络设备",
    )
    ]

class Project(models.Model):
    service_name = models.CharField(max_length=60, blank=True, null=True, verbose_name=u'项目名')
    
    def __unicode__(self):
        return self.service_name

    class Meta:
        verbose_name = u"项目列表"
        verbose_name_plural = verbose_name
        app_label = 'assets'


SERVER_STATUS = (
    (1, u"未上架"),
    (2, u"已上架"),
    (3, u"上架中"),
    (4, u"报废"),
)

PHYS_STATUS = (
    (0, u"物理机"),
    (1, u"虚拟机"),
)

ENVIRONMENT = [(i, i) for i in (u"tadu", u"tuosi")]

class Server(models.Model):
    uuid = UUIDField(auto=True, primary_key=True)
    device_type = models.IntegerField(max_length=64, choices=DEVICE_TYPES, default=1, verbose_name=u'设备类型')
    hostname = models.CharField(max_length=100, blank=True, null=True, verbose_name=u"主机名")
    eth1 = models.IPAddressField(blank=True, null=True, verbose_name=u'网卡1')
    eth2 = models.IPAddressField(blank=True, null=True, verbose_name=u'网卡2')
    service = models.ManyToManyField(Project, blank=True, null=True, verbose_name=u'所属项目')
    idc = models.ForeignKey(IDC, blank=True, null=True, verbose_name=u'机房', on_delete=models.SET_NULL)
    cabinet = models.CharField(max_length=32, blank=True, null=True, verbose_name=u'机柜号')
    cabinet_id = models.IntegerField(blank=True, null=True, verbose_name=u'服务器位置')
    height = models.IntegerField(blank=True, null=True, verbose_name=u'服务器高度')
    #create_time = models.DateTimeField(verbose_name=u'上架时间',default=time.strftime('%Y-%m-%d %H:%M:%S'))
    create_time = models.DateField(default='2001-01-01',verbose_name=u'上架时间')
    status = models.IntegerField(verbose_name=u"机器状态", choices=SERVER_STATUS, default=1, blank=True)
    vm = models.ForeignKey("self", blank=True, null=True, verbose_name=u"虚拟机父主机")
    type = models.IntegerField(default=0, blank=True, choices=PHYS_STATUS,max_length=2,verbose_name=u'主机类型',)
    env = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"环境", choices=ENVIRONMENT)
    model = models.CharField(default='Dell R730', max_length=64, choices=MODELS, verbose_name=u'设备型号')
    sn = models.CharField(max_length=32, blank=True, null=True, verbose_name=u'序列号')

    def __unicode__(self):
        return self.eth1

    class Meta:
        ordering = ['eth1']
        verbose_name = u"服务器列表"
        verbose_name_plural = verbose_name
        app_label = 'assets'

class ShoppingList(models.Model):
    uuid = models.AutoField(primary_key=True,verbose_name=u'ID')
    device_type = models.IntegerField(max_length=64, choices=DEVICE_TYPES, default=1, verbose_name=u'设备类型')
    vendor = models.IntegerField(max_length=64,choices=VENDORS,verbose_name=u'设备厂商')
    model = models.CharField(max_length=64,choices=MODELS,verbose_name=u'设备型号')
    detail = models.TextField(blank=True, null=True, verbose_name=u"详细配置")
    price = models.IntegerField(verbose_name=u"单价")
    nums = models.IntegerField(verbose_name=u"数量")
    total_price = models.IntegerField(verbose_name=u"总价")
    supplier = models.CharField(max_length=32, verbose_name=u'供货商')
    contacts = models.CharField(max_length=32, verbose_name=u"联系电话")
    #buy_date = models.DateTimeField(auto_now_add=False,verbose_name=u"采购日期")
    buy_date = models.DateField(default='2001-01-01', verbose_name=u"采购日期")
    sn = models.TextField(blank=True, null=True, verbose_name=u'序列号')
    comment = models.TextField(blank=True, null=True, verbose_name=u"备注")
    # ipaddr = models.IPAddressField(verbose_name=u"IP地址")
    ipaddr = models.ManyToManyField(Server, blank=True, null=True, verbose_name=u'IP地址')

    def __unicode__(self):
        return self.model

    class Meta:
        verbose_name = u"采购表"
        verbose_name_plural = verbose_name
        app_label = 'assets'

class HostRecord(models.Model):
    """ 主机修改记录model """
    uuid = UUIDField(auto=True, primary_key=True)
    host = models.ForeignKey(Server)
    user = models.CharField(max_length=30, null=True)
    time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.host.hostname

    class Meta:
        verbose_name = u"主机修改记录"
        verbose_name_plural = verbose_name
        app_label = 'assets'

    
class OnlineRecord(models.Model):
    uuid = UUIDField(auto=True, primary_key=True)
    project = models.ForeignKey(Project, blank=False, verbose_name=u'所属项目')
    URL = models.URLField(blank=False,verbose_name="网址")
    version = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'MD5值')
    online_time = models.DateTimeField(auto_now=True,verbose_name=u'上线时间')
    person = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'上线人员')

    def __unicode__(self):
        return self.project

    class Meta:
        verbose_name = u"上线历史记录"
        verbose_name_plural = verbose_name
        app_label = 'assets'
