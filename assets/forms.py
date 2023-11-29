# coding:utf-8
from django import forms
from assets.models import IDC,ShoppingList,Server,Project,OnlineRecord

# from django.contrib.admin import widgets
# from django.forms.extras.widgets import SelectDateWidget
# class PostForm(forms.Form):
#     date = forms.DateTimeField(widget=widgets.AdminDateWidget(), label=u'时间')


class IdcForm(forms.ModelForm):
    class Meta:
        model = IDC
        # fields = ['name', "bandwidth", "operator", 'type', 'linkman', 'phone', 'network', 'address', 'comment']
        fields = "__all__"


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        # fields = ['vendor', "model", "detail",'ipaddr','sn', 'price', 'nums', 'total_price', 'supplier', 'contacts','buy_date','comment']
        fields = "__all__"
        #exclude = ['uuid']


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        # fields = ["sn", "hostname", "eth1", "eth2", "service", "idc","vm","type","cabinet", "cabinet_id", "height","create_time","status"]
        fields = "__all__"
