# coding:utf-8
from django import forms
from assets.models import Project,OnlineRecord


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['id','service_name']


class OnlineRecordForm(forms.ModelForm):
    class Meta:
        model = OnlineRecord
        fields = ['project','URL','version']
