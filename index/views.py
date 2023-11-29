# coding=UTF-8
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from assets.models import Server, IDC, Project, HostRecord
from django.contrib.auth.models import User
from assets.new_api import get_zdata
from index.index_api import format_time
from swan.models import OnlineLog


@login_required
def index(request):
    users = User.objects.count()
    hosts = Server.objects.count()
    project = Project.objects.count()
    idc_count = IDC.objects.all().count()
    zdata = get_zdata(request.user.username)
    swan_onlinelogs = OnlineLog.objects.all().order_by("-optime")[:10]
    start_time, stop_time = format_time()
    today_onlines = OnlineLog.objects.filter(tag=1, optime__gte=stop_time)
    today_online_data = {}
    for i in today_onlines:
        pname = i.pname
        if today_online_data.get(pname, False):
            today_online_data[i.pname]["count"] += 1
        else:
            today_online_data[i.pname] = {"count": 1}
    return render_to_response('index/dashboard.html', locals(), context_instance=RequestContext(request))


@login_required
def ztree_host_detail(request):
    """ 主机详情 """
    uuid = request.GET.get('uuid', '')
    ip = request.GET.get('ip', '')
    zdata = get_zdata(request.user.username)
    if uuid:
        host = get_object_or_404(Server, uuid=uuid)
    elif ip:
        host = get_object_or_404(Server, eth1=ip)

    host_record = HostRecord.objects.filter(host=host).order_by('-time')
    return render_to_response('assets/host_detail.html', locals(), context_instance=RequestContext(request))

@login_required
def docs(request):
    return render_to_response('index/docs.html', locals(), context_instance=RequestContext(request))