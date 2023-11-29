# coding:utf-8
import datetime
import json
import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from assets.models import Server, Project, SERVER_STATUS, OnlineRecord
from assets.new_api import pages, sort_ipaddr
from forms import ProjectForm, OnlineRecordForm
from salt.views import update_command, log_command, log_handle_command, online_command, run_command
from swan.models import OnlineLog
from swan.swan_api import add_onlinerecordlog, add_onlinelog


class RaiseError(Exception):
    pass


def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))


@login_required
def project_add(request):
    if request.method == 'POST':
        uf = ProjectForm(request.POST)
        if uf.is_valid():
            project_name = uf.cleaned_data['service_name']
            if Project.objects.filter(service_name=project_name):
                emg = u'添加失败, 此项目 %s 已存在!' % project_name
                return my_render('swan/project_add.html', locals(), request)
            smg = u'项目 %s 添加成功!' % project_name
            uf.save()
    else:
        uf = ProjectForm()
    return render_to_response('swan/project_add.html', locals(), context_instance=RequestContext(request))


@login_required
def project_list(request):
    projects = Project.objects.all()
    return render_to_response('swan/project_list.html', locals(), context_instance=RequestContext(request))


@login_required
def project_edit(request):
    id = request.GET.get('id', '')
    proj = get_object_or_404(Project, id=id)
    if request.method == 'POST':
        uf = ProjectForm(request.POST, instance=proj)
        if uf.is_valid():
            uf.save()
            return HttpResponseRedirect("/swan/project_list/")
    else:
        uf = ProjectForm(instance=proj)
        return my_render('swan/project_edit.html', locals(), request)


@login_required
def project_del(request):
    id = request.GET.get('id', '')
    project = get_object_or_404(Project, id=id)
    project_name = project.service_name
    project.delete()
    return HttpResponseRedirect('/swan/project_list/')


@login_required
@csrf_exempt
def project_upload(request):
    if request.method == 'POST':
        uf = OnlineRecordForm(request.POST)
        if uf.is_valid():
            # online_time = uf.cleaned_data['online_time']
            # if OnlineRecord.objects.filter(online_time=online_time):
            #     emg = u'添加失败, 此版本 %s 已存在!' % version
            #     return my_render('swan/project_upload.html', locals(), request)
            smg = u'添加成功!'
            # project_name = uf.cleaned_data['project']
            URL = uf.cleaned_data['URL']
            MD5 = uf.cleaned_data['version']
            logstr = "在项目记录页面添加了一条记录"
            add_onlinerecordlog(request.user.username, logstr, URL, MD5)
            uf.save()
        else:
            emg = u'添加失败!'
   
    uf = OnlineRecordForm()
    return my_render('swan/project_upload.html', locals(), request)


@login_required
def project_update(request):
    person = request.user.username
    uuid = request.GET.get("uuid", '')
    jiramd5 = request.GET.get("jiramd5", '')
    project = request.GET.get("project", '')
    onlineobj = OnlineRecord.objects.get(uuid=uuid)
    war = onlineobj.URL
    onlineobj.person = person
    onlineobj.save()
    if project == 'cms':
        host = 'zabbix.tadu.com'
    else:
        host = 'minion'
    ret,ret2 = update_command(host,project,war)

    try:
        back_result = ret[0][host]
    except Exception,e:
        back_result = ret
    try:
        md5 = ret2[0][host]
    except Exception,e:
        md5 = ret2

    md5 = md5.split()[0]
    if jiramd5 == md5:
        flag = "成功"
        logstr = "在项目记录页面上传记录,成功!"
    else:
        flag = "失败"
        logstr = "在项目记录页面上传记录,失败!"
    add_onlinerecordlog(person, logstr, war, onlineobj.version)
    return my_render('swan/project_update.html', locals(), request)


@login_required
def project_rollback(request):
    uuid = request.GET.get("uuid", '')
    onlineobj = OnlineRecord.objects.get(uuid=uuid)
    addr = onlineobj.URL
    romd5 = onlineobj.version
    if request.method == 'POST':
        uf_post = OnlineRecordForm(request.POST)
        if uf_post.is_valid():
            smg = u'回滚成功!'
            logstr = "在项目记录页面回滚了一条记录"
            add_onlinerecordlog(request.user.username, logstr, addr, romd5)
            uf_post.save()
        else:
            emg = u'回滚失败!'

    return my_render('swan/project_rollback.html', locals(), request)


@login_required
def project_remove(request):
    uuid = request.GET.get('uuid', '')
    record = get_object_or_404(OnlineRecord, uuid=uuid)
    logstr = "在项目记录页面删除了一条记录"
    add_onlinerecordlog(request.user.username, logstr, record.URL, record.version)
    record.delete()
    return HttpResponseRedirect('/swan/project_history/')


@login_required
def project_history(request):
    records = OnlineRecord.objects.all().order_by("-online_time")
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(records, request)
    return render_to_response('swan/project_history.html', locals(), context_instance=RequestContext(request))


@login_required
def project_history_filter(request):
    pid = request.GET.get('pid','')
    # s_url用于搜索页面的分页功能
    s_url = request.get_full_path()
    if 'page' in s_url:
        s_url = re.sub('&page=\d','',s_url)
    search = 1
    records = OnlineRecord.objects.filter(project=pid).order_by("-online_time")
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(records, request)
    return render_to_response('swan/project_history_filter.html', locals(), context_instance=RequestContext(request))


@login_required
def project_deploy(request):
    business_name = request.GET.get('change_business', 'all')
    hosttype = request.GET.get('change_type', '')

    if business_name != 'all' and hosttype != '':
        hosts = Server.objects.all().filter(service__service_name=business_name).filter(type=hosttype).order_by("eth1")
    elif business_name != 'all' and hosttype == '':
        hosts = Server.objects.all().filter(service__service_name=business_name).order_by("eth1")
    elif business_name == 'all' and hosttype != '':
        hosts = Server.objects.all().filter(type=hosttype).order_by("eth1")
    else:
        hosts = Server.objects.all().order_by("eth1")

    server_type = Project.objects.all()
    server_status = SERVER_STATUS
    server_list_count = hosts.count()
    physics = Server.objects.filter(vm__isnull=True).count()
    vms = Server.objects.filter(vm__isnull=False).count()
    servers = sort_ipaddr(hosts)
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(servers, request)
    return render_to_response('swan/project_deploy.html', locals(), context_instance=RequestContext(request))


@login_required
def project_log(request):
    uuid = request.GET.get('uuid', '')
    pid = request.GET.get('project', '')
    serverobj = Server.objects.get(uuid=uuid)
    hostname = serverobj.hostname
    
    if pid:
        project = pid
    else:
        data = serverobj.service.all()
        business_all = []
        if data:
            for i in data:
                business_all.append(i.service_name)
        project = business_all[0]

    logstr = "在项目发布页面点击了日志按钮"
    result = "发布页面日志按钮"
    add_onlinelog(request.user.username, logstr, "tail -f catalina.out", 3, project, uuid, hostname, result)
    linenum,result1 = log_command(hostname,project)
    return render_to_response('swan/project_log.html', locals(), context_instance=RequestContext(request))


"""
前端页面使用两个ajax时会用到
@login_required
def get_log_endline(request):
    hostname = request.GET.get('hid')
    linenum = request.GET.get('linenum')
    project = request.GET.get('pid')
    endline = get_endline_command(hostname,project,linenum)
    return HttpResponse(endline)
"""


@login_required
def project_log_handle(request):
    hostname = request.GET.get('hid')
    linenum = request.GET.get('linenum')
    project = request.GET.get('pid')
    endline,result2 = log_handle_command(hostname,project,linenum)
    callback = []
    callback.append(endline)
    callback.append(result2)
    return HttpResponse(json.dumps(callback))


@login_required
def project_online(request):
    uuid = request.GET.get('uuid', '')
    serverobj = Server.objects.get(uuid=uuid)
    hostname = serverobj.hostname
    data = serverobj.service.all()
    business_all = []
    if data:
        for i in data:
            business_all.append(i.service_name)
    project = business_all[0]

    logstr = "在项目发布页面点击了上线按钮"
    command = "puppet agent -t"
    try:
        result, command = online_command(hostname,project)
    except Exception, e:
        result = "上线异常"
    add_onlinelog(request.user.username, logstr, command, 1, project, uuid, hostname, result)

    return render_to_response('swan/project_online.html', locals(), context_instance=RequestContext(request))


@login_required
def execute_command(request):
    uuid = request.GET.get('uuid', '')
    return render_to_response('swan/execute_command.html', locals(), context_instance=RequestContext(request))


@csrf_exempt
@login_required
def execute_command2(request):
    uuid = request.POST.get('uuid','')
    command = request.POST.get('command','')
    serverobj = Server.objects.get(uuid=uuid)
    hostname = serverobj.hostname
    data = serverobj.service.all()
    business_all = []
    if data:
        for i in data:
            business_all.append(i.service_name)
    project = business_all[0]

    logstr = "在项目发布页面点击了执行命令按钮"
    result = run_command(hostname, command)
    if result is False:
        result = "你没有权限执行此命令: %s" %command

    add_onlinelog(request.user.username, logstr, command, 2, project, uuid, hostname, result)
    return HttpResponse(json.dumps(result))


# @login_required
# def project_online_batch(request):
#     ids = str(request.GET.get('ids',''))
#     results = {}
#     hostnames = ids.split(',')
#     for hostname in hostnames:
#         result = online_command(hostname)
#         results[hostname]=result
#
#     return render_to_response('swan/project_online_batch.html', locals(), context_instance=RequestContext(request))

@login_required
def filter_online_log(request, pname):
    """
    异步请求返回当前项目已添加发布按钮
    :param request:
    :return:
    """
    date = request.GET.get("date")

    day = datetime.datetime.strptime(date, '%Y-%m-%d')
    log_data = OnlineLog.objects.filter(pname=pname, optime__gte=day).order_by("-optime")

    return render_to_response('swan/filter_online_log.html', locals(), context_instance=RequestContext(request))


@login_required
def push_zabbix(request):
    hosts = Server.objects.all().order_by("eth1")
    server_type = Project.objects.all()
    server_status = SERVER_STATUS
    server_list_count = hosts.count()
    physics = Server.objects.filter(vm__isnull=True).count()
    vms = Server.objects.filter(vm__isnull=False).count()
    servers = sort_ipaddr(hosts)
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(servers, request)
    return render_to_response('swan/push_zabbix.html', locals(), context_instance=RequestContext(request))


@login_required
def push_cmd(request):
    hosts = Server.objects.all().order_by("eth1")
    server_type = Project.objects.all()
    server_status = SERVER_STATUS
    server_list_count = hosts.count()
    physics = Server.objects.filter(vm__isnull=True).count()
    vms = Server.objects.filter(vm__isnull=False).count()
    servers = sort_ipaddr(hosts)
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(servers, request)
    return render_to_response('swan/push_cmd.html', locals(), context_instance=RequestContext(request))


@login_required
def push_module(request):
    hosts = Server.objects.all().order_by("eth1")
    server_type = Project.objects.all()
    server_status = SERVER_STATUS
    server_list_count = hosts.count()
    physics = Server.objects.filter(vm__isnull=True).count()
    vms = Server.objects.filter(vm__isnull=False).count()
    servers = sort_ipaddr(hosts)
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(servers, request)
    return render_to_response('swan/push_module.html', locals(), context_instance=RequestContext(request))
