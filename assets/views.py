# coding:utf-8
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from assets.models import IDC,ShoppingList,Server,Project,MODELS,SERVER_STATUS,HostRecord,DEVICE_TYPES
from assets.new_api import pages, sort_ipaddr, get_zdata
from forms import IdcForm,ShoppingListForm,ServerForm
from django.http.response import HttpResponse

from django.db.models import Q
from pdf import rpt, excel_output
import ast,time


class RaiseError(Exception):
    pass


def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))


def get_diff(obj1, obj2):
    fields = ['service']
    no_check_fields = ['supplier', 'contacts', 'status']
    d1, d2 = obj1, dict(obj2.iterlists())

    info = {}
    for k, v in d1.items():
        if k in fields:
            if d2.get(k):
                d2_value = d2[k]
            else:
                d2_value = u''
        elif k in no_check_fields:
            continue
        else:
            d2_value = d2[k][0]

        if not v and k != 'type':
            if v is False:
                pass
            else:
                v = u''

        if isinstance(v,list):
            v.sort()
            if not d2_value:
                d2_value = []
            d2_value.sort()
            if v != d2_value:
                info.update({k: [v, d2_value]})
        else:
            if str(v) != str(d2_value):
                info.update({k: [v, d2_value]})

    for k, v in info.items():
        if v == [None, u'']:
            info.pop(k)
    return info


def db_to_record(username, host, info):
    text_list = []
    for k, v in info.items():
        field = Server._meta.get_field_by_name(k)[0].verbose_name
        if k == 'idc':
            old = IDC.objects.filter(uuid=v[0])
            new = IDC.objects.filter(uuid=v[1])
            if old:
                name_old = old[0].name
            else:
                name_old = u'无'
            if new:
                name_new = new[0].name
            else:
                name_new = u'无'
            text = field + u'由 ' + name_old + u' 更改为 ' + name_new
        elif k == 'service':
            old, new = [], []
            for s in v[0]:
                project_name = Project.objects.get(id=s).service_name
                old.append(project_name)
            for s in v[1]:
                project_name = Project.objects.get(id=s).service_name
                new.append(project_name)
            text = field + u'由 ' + ','.join(old) + u' 更改为 ' + ','.join(new)
        elif k == 'vm':
            old, new = [], []
            if v[0] and not v[1]:
                old_ip = Server.objects.get(uuid=v[0]).eth1
                old.append(old_ip)
                text = field + u'由 空' + ','.join(old) + u' 更改为 空'
            elif not v[0] and v[1]:
                new_ip = Server.objects.get(uuid=v[1]).eth1
                new.append(new_ip)
                text = field + u'由 空' + u' 更改为 ' + ','.join(new)
            else:
                old_ip = Server.objects.get(uuid=v[0]).eth1
                old.append(old_ip)
                new_ip = Server.objects.get(uuid=v[1]).eth1
                new.append(new_ip)
                text = field + u'由 ' + ','.join(old) + u' 更改为 ' + ','.join(new)

        elif k == 'type':
            if v[1] == 0:
                text = field + u'由 虚拟机' + u' 更改为 物理机'
            else:
                text = field + u'由 物理机' + u' 更改为 虚拟机'
        else:
            if str(v[0]):
                if str(v[1]):
                    text = field + u'由 ' + str(v[0]) + u' 更改为 ' + str(v[1])
                else:
                    text = field + u'由 ' + str(v[0]) + u' 更改为 空'
            else:
                text = field + u'由 空 ' + str(v[0]) + u' 更改为 ' + str(v[1])
        text_list.append(text)

    # 存入数据库，列表中的中文元素会转码成utf-8，需要把列表转换成json字符串
    # 从数据库取出的json数据是unicode字符串，需要先转码成utf-8，然后用ast.literal_eval()函数转换成列表
    text_list = json.dumps(text_list, encoding='UTF-8', ensure_ascii=False)
    if len(text_list) != 0:
        HostRecord.objects.create(host=host, user=username, content=text_list)


@login_required
def idc_add(request):
    """ 添加IDC """
    if request.method == 'POST':
        init = request.GET.get("init", False)

        uf = IdcForm(request.POST)
        if uf.is_valid():
            idc_name = uf.cleaned_data['name']
            if IDC.objects.filter(name=idc_name):
                emg = u'添加失败, 此IDC %s 已存在!' % idc_name
                return my_render('assets/idc_add.html', locals(), request)
            uf.save()
            if not init:
                return HttpResponseRedirect("/assets/idc_list/")
            else:
                return HttpResponseRedirect('/assets/server/type/add/?init=true')

    else:
        uf = IdcForm()
    return render_to_response('assets/idc_add.html', locals(), context_instance=RequestContext(request))


@login_required
def idc_list(request):
    idcs = IDC.objects.all()
    return render_to_response('assets/idc_list.html', locals(), context_instance=RequestContext(request))


@login_required
def idc_edit(request):
    uuid = request.GET.get('uuid', '')
    idc = get_object_or_404(IDC, uuid=uuid)
    if request.method == 'POST':
        uf = IdcForm(request.POST, instance=idc)
        if uf.is_valid():
            uf.save()
            return HttpResponseRedirect("/assets/idc_list/")
    else:
        uf = IdcForm(instance=idc)
        return my_render('assets/idc_edit.html', locals(), request)


@login_required
def idc_del(request):
    uuid = request.GET.get('uuid', '')
    idc = get_object_or_404(IDC, uuid=uuid)
    idc_name = idc.name
    idc.delete()
    return HttpResponseRedirect('/assets/idc_list/')


@login_required
def shopping_list(request):
    sls = ShoppingList.objects.all().order_by("buy_date")
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(sls, request)
    return render_to_response('assets/shopping_list.html', locals(), context_instance=RequestContext(request))

@login_required
def shopping_info_ajax(request):
    """ 采购表搜索 """
    keyword = request.GET.get('keyword', '')
    if keyword:
        SN = ShoppingList.objects.filter(sn__contains=keyword)
        IP = ShoppingList.objects.filter(ipaddr__eth1__contains=keyword)
        if  SN:
            sls = SN
        elif IP:
            sls = IP
        else:
            sls = ""
    else:
        sls = ShoppingList.objects.all().order_by("buy_date")
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(sls, request)
    return render_to_response('assets/shopping_info_ajax.html',locals(), context_instance=RequestContext(request))

@login_required
def shopping_add(request):
    if request.method == 'POST':
        init = request.GET.get("init", False)
        uf = ShoppingListForm(request.POST)
        if uf.is_valid():
            sn_id = uf.cleaned_data['sn']
            if ShoppingList.objects.filter(sn=sn_id):
                emg = u'添加失败, 此采购项 %s 已存在!' % sn_id
                return my_render('assets/shopping_add.html', locals(), request)
            uf.save()
            ip = uf.cleaned_data['ipaddr']
            smg = u'主机%s添加成功!' % ip
            return render_to_response('assets/shopping_add.html', locals(), context_instance=RequestContext(request))
    else:
        uf = ShoppingListForm()
    return render_to_response('assets/shopping_add.html', locals(), context_instance=RequestContext(request))


@login_required
def shopping_edit(request):
    uuid = request.GET.get('uuid', '')
    result = get_object_or_404(ShoppingList, uuid=uuid)

    if request.method == 'POST':
        uf = ShoppingListForm(request.POST, instance=result)
        if uf.is_valid():
            uf.save()
            return HttpResponseRedirect("/assets/shopping_list/")
    else:
        uf = ShoppingListForm(instance=result)
        return my_render('assets/shopping_edit.html', locals(), request)


@login_required
def shopping_del(request):
    uuid = request.GET.get('uuid', '')
    slobj = get_object_or_404(ShoppingList, uuid=uuid)
    slobj.delete()
    return HttpResponseRedirect('/assets/shopping_list/')


@login_required
def host_list(request):
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

    idcs = IDC.objects.filter()
    server_type = Project.objects.all()
    dtypes = DEVICE_TYPES
    brands = MODELS
    server_status = SERVER_STATUS
    server_list_count = hosts.count()
    physics = Server.objects.filter(vm__isnull=True).count()
    vms = Server.objects.filter(vm__isnull=False).count()

    servers = sort_ipaddr(hosts)

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(servers, request)
    return render_to_response('assets/host_list.html', locals(), context_instance=RequestContext(request))

@login_required
@csrf_exempt
def host_search(request):
    """ 条件搜索ajax """

    idcs = IDC.objects.filter()
    server_type = Project.objects.all()
    server_status = SERVER_STATUS

    idc_name = request.GET.get('change_idc', '')
    business_name = request.GET.get('change_business', '')
    status = request.GET.get('change_status', False)
    dtype = request.GET.get('change_dtype', False)

    if status:
        status = int(status)
    else:
        status = ""

    type = request.GET.get('change_type', '')

    if not idc_name and not status and business_name == 'all' and not type and not dtype:
        select_number = 0
    else:
        select_number = 1


    keyword = request.GET.get('keyword', '')
    s_url = request.get_full_path()

    if select_number == 0:
        servers = Server.objects.all()

    elif business_name != 'all' and not idc_name and not status:
        project_obj = Project.objects.get(service_name=business_name)
        servers = Server.objects.filter(service=project_obj)

    elif business_name == 'all' and idc_name and not status:
        servers = Server.objects.filter(idc__name__contains=idc_name)

    elif business_name == 'all' and not idc_name and status:
        servers = Server.objects.filter(status=status)

    elif business_name != 'all' and idc_name and not status:
        project_obj = Project.objects.get(service_name=business_name)
        servers = Server.objects.filter(service=project_obj,
                                        idc__name__contains=idc_name)

    elif business_name != 'all' and not idc_name and status:
        project_obj = Project.objects.get(service_name=business_name)
        servers = Server.objects.filter(service=project_obj,
                                        status=status)

    elif business_name == 'all' and idc_name and status:
        servers = Server.objects.filter(status=status,
                                        idc__name__contains=idc_name)

    elif idc_name and status and business_name != 'all':       
        project_obj = Project.objects.get(service_name=business_name)
        servers = Server.objects.filter(service=project_obj,
                                    idc__name__contains=idc_name,
                                    status=status)
    # TODO:type and dtype search is incomplete!!!
    elif type:
        servers = Server.objects.filter(type=type)
    elif dtype:
        servers = Server.objects.filter(device_type=dtype)
    else:
        pass

    if keyword and select_number == 1:
        servers = servers.filter(
                             Q(hostname__contains=keyword) |
                             Q(eth1__contains=keyword) |
                             Q(eth2__contains=keyword) |                       
                             Q(service__service_name__contains=keyword) |
                             Q(idc__name__contains=keyword) |
                             Q(vm__eth1__contains=keyword) |
                             Q(env__contains=keyword) |
                             Q(model__contains=keyword) |
                             Q(sn__contains=keyword) |
                             Q(cabinet__contains=keyword))
                             # Q(cabinet_id=keyword)
                             # Q(height=keyword) )
    elif keyword:
        servers = Server.objects.filter(
                             Q(hostname__contains=keyword) |
                             Q(eth1__contains=keyword) |
                             Q(eth2__contains=keyword) |                       
                             Q(service__service_name__contains=keyword) |
                             Q(idc__name__contains=keyword) |
                             Q(vm__eth1__contains=keyword) |
                             Q(env__contains=keyword) |
                             Q(model__contains=keyword) |
                             Q(sn__contains=keyword) |
                             Q(cabinet__contains=keyword))
                             # Q(cabinet_id=keyword) )
                             # Q(height=keyword) )

    servers = sort_ipaddr(servers)

    search_status = request.GET.get("_search", False)
    search_output_name = request.GET.get("name", False)
    if search_status and search_output_name:
        if search_output_name == 'pdf':
            s = rpt(servers)
            if s:
                data = "pdf"
                return render_to_response('assets/download.html', locals(), context_instance=RequestContext(request))

        if search_output_name == 'excel':
            s = excel_output(servers)
            if s:
                data = "execl"
                return render_to_response('assets/download.html', locals(), context_instance=RequestContext(request))

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(servers, request)
    if 'project_ajax' in request.get_full_path():
        s_url = s_url.replace('change_project_ajax', 'host_search')
        return my_render('swan/project_info_ajax.html', locals(), request)
    elif 'ajax' in request.get_full_path():
        s_url = s_url.replace('change_info_ajax', 'host_search')
        return my_render('assets/host_info_ajax.html', locals(), request)
    else:
        servers = Server.objects.all()
        idcs = IDC.objects.filter()
        server_type = Project.objects.all()
        server_status = SERVER_STATUS
        server_list_count = servers.count()
        search = 1
        return my_render('assets/host_list.html', locals(), request)


@login_required
def host_add(request):
    physicIP = request.GET.get('physicIP','')
    if physicIP:
        server_obj = Server.objects.get(eth1=physicIP)
        rlist = {'cabinet':server_obj.cabinet,'cabinet_id':server_obj.cabinet_id,'height':server_obj.height,'create_time':server_obj.create_time.strftime('%Y-%m-%d')}
        return HttpResponse(json.dumps(rlist))

    uf = ServerForm()
    projects = Project.objects.all()
    #mytime = time.strftime('%Y/%m/%d %H:%M')
    mytime = time.strftime('%Y-%m-%d')

    if request.method == 'POST':
        uf = ServerForm(request.POST)
        physics = request.POST.get('physics', '')
        ip = request.POST.get('eth1', '')
        if Server.objects.filter(eth1=ip):
            emg = u'添加失败, 该IP %s 已存在!' % ip
            return my_render('assets/host_add.html', locals(), request)
        if uf.is_valid():
            zw = uf.save(commit=False)
            status = uf.cleaned_data['status']
            if physics:
                try:
                    physics_host = get_object_or_404(Server, eth1=physics)
                    zw.vm = physics_host
                    zw.type = 1
                except Exception,e:
                    smg = u'物理机%s不存在!' % physics
                    return render_to_response('assets/host_add.html', locals(), context_instance=RequestContext(request))
            else:
                zw.type = 0
            zw.save()
            uf.save_m2m()
            smg = u'主机%s添加成功!' % ip
            return render_to_response('assets/host_add.html', locals(), context_instance=RequestContext(request))
    
    return render_to_response('assets/host_add.html', locals(), context_instance=RequestContext(request))


@csrf_exempt
@login_required
def host_del_batch(request):
    """ 批量删除主机 """
    ids = str(request.POST.get('ids'))
    for uuid in ids.split(','):
        host = get_object_or_404(Server, uuid=uuid)
        host.delete()
    return HttpResponseRedirect('/assets/host_list/')


@login_required
def host_del(request):
    """ 删除主机 """
    uuid = request.GET.get('uuid', '')
    host = get_object_or_404(Server, uuid=uuid)
    # host.business.clear()
    host.delete()
    return HttpResponseRedirect('/assets/host_list/')

@login_required
def host_edit(request):
    """ 修改主机 """
    uuid = request.GET.get('uuid')
    host = get_object_or_404(Server, uuid=uuid)
    uf = ServerForm(instance=host)
    project_all = Project.objects.all()
    project_host = host.service.all()
    #mytime = host.create_time.strftime('%Y/%m/%d %H:%M')
    mytime = host.create_time.strftime('%Y-%m-%d')

    projects = [p for p in project_all if p not in project_host]

    username = request.user.username
    if request.method == 'POST':
        physics = request.POST.get('physics', '')
        uf_post = ServerForm(request.POST, instance=host)

        if uf_post.is_valid():
            '''
            zw = uf_post.save(commit=False)
            request.POST = request.POST.copy()
            zw.save()
            uf_post.save_m2m()
            
            request.POST = request.POST.copy()
            uf_post.save()
            '''
            zw = uf_post.save(commit=False)
            request.POST = request.POST.copy()
            if physics:
                try:
                    physics_host = get_object_or_404(Server, eth1=physics)
                except Exception,e:
                    smg = u'物理机%s不存在!' % physics
                    return render_to_response('assets/host_edit.html', locals(), context_instance=RequestContext(request))
                
                request.POST['vm'] = physics_host.uuid
                request.POST['type'] = 1
                if host.vm:
                    if str(host.vm.eth1) != str(physics):
                        zw.vm = physics_host
                else:
                    zw.vm = physics_host
                zw.type = 1
            else:
                request.POST['vm'] = ''
                request.POST['type'] = 0
                zw.type = 0
            zw.save()
            uf_post.save_m2m()

            # 修改表单中获取的service的类型
            s = uf_post.__dict__.get('initial')['service']
            s2 = []
            for i in s:
                s2.append(unicode(i))
            uf_post.__dict__.get('initial')['service'] = s2

            # 修改上架时间的格式
            #stime = uf_post.__dict__.get('initial')['create_time'].strftime('%Y/%m/%d %H:%M')
            stime = uf_post.__dict__.get('initial')['create_time'].strftime('%Y-%m-%d')
            uf_post.__dict__.get('initial')['create_time'] = stime

            # 修改主机类型为unicode
            # s4 = uf_post.__dict__.get('initial')['type']
            # s3 = []
            # s3.append(unicode(s4))
            # uf_post.__dict__.get('initial')['type'] = s3

            new_host = get_object_or_404(Server, uuid=uuid)

            info = get_diff(uf_post.__dict__.get('initial'), request.POST)
            db_to_record(username, host, info)
            
            return HttpResponseRedirect('/assets/host_list')
            # return render_to_response('assets/host_edit.html', locals(), context_instance=RequestContext(request))
    return render_to_response('assets/host_edit.html', locals(), context_instance=RequestContext(request))


@login_required
def host_detail(request):
    """ 主机详情 """
    uuid = request.GET.get('uuid', '')
    ip = request.GET.get('ip', '')
    # zdata = get_zdata(request.user.username)
    if uuid:
        host = get_object_or_404(Server, uuid=uuid)
    elif ip:
        host = get_object_or_404(Server, eth1=ip)
    
    host_record = HostRecord.objects.filter(host=host).order_by('-time')
    return render_to_response('assets/host_detail.html', locals(), context_instance=RequestContext(request))

@login_required
@csrf_exempt
def host_edit_batch(request):
    """ 批量修改主机 """
    uf = ServerForm()
    username = request.user.username
    projects = Project.objects.all()
    if request.method == 'POST':

        ids = str(request.GET.get('uuid', ''))
        idc = request.POST.get('idc', '')
        env = request.POST.get('env', '')
        model = request.POST.get('model', '')
        business = request.POST.getlist('business', '')
        cabinet = request.POST.get('cabinet', '')
        create_time = request.POST.get('create_time', '')
        uuid_list = ids.split(",")

        for uuid in uuid_list:
            record_list = []
            host = get_object_or_404(Server, uuid=uuid)

            if idc:
                if host.idc != idc:
                    if not host.idc:
                        text = u'IDC' + u'由 ' + "none" + u' 更改为 ' + get_idc.name
                    else:
                        text = u'IDC' + u'由 ' + host.idc.name + u' 更改为 ' + get_idc.name
                    record_list.append(text)
                    host.idc = get_idc

            if env:
                if host.env != env:
                    if not host.env:
                        text = u'设备型号' + u'由 ' + "none" + u' 更改为 ' + env
                    else:
                        text = u'设备型号' + u'由 ' + host.env + u' 更改为 ' + env
                    record_list.append(text)
                    host.env = env

            if model:
                if host.model != model:
                    if not host.model:
                        text = u'设备型号' + u'由 ' + "none" + u' 更改为 ' + model
                    else:
                        text = u'设备型号' + u'由 ' + host.model + u' 更改为 ' + model
                    record_list.append(text)
                    host.model = model

            if business:
                old, new, project_list = [], [], []
                for s in host.service.all():
                    project_name = s.service_name
                    old.append(project_name)
                for s in business:
                    project = Project.objects.get(id=s)
                    project_name = project.service_name
                    new.append(project_name)
                    project_list.append(project)
                if old != new:
                    text = u'所属业务' + u'由 ' + ','.join(old) + u' 更改为 ' + ','.join(new)
                    record_list.append(text)
                    host.service = project_list

            if cabinet:
                if not host.cabinet:
                    info = u'无'
                else:
                    info = host.cabinet
                if cabinet != host.cabinet:
                    text = '机柜号' + u'由 ' + info + u' 更改为 ' + cabinet
                    record_list.append(text)
                    host.cabinet = cabinet

            if create_time:
                info = host.create_time

                if  str(host.create_time) != str(create_time):
                    text = '机柜号' + u'由 ' + str(info )+ u' 更改为 ' + str(create_time)
                    record_list.append(str(text))
                    host.create_time = create_time

            if len(record_list) != 0:
                host.save()
                HostRecord.objects.create(host=host, user=username, content=record_list)

        return my_render('assets/host_edit_batch_ok.html', locals(), request)
    return my_render('assets/host_edit_batch.html', locals(), request)

@login_required
@csrf_exempt
def host_add_batch(request):
    """ 批量添加主机 """
    if request.method == 'POST':
        multi_hosts = request.POST.get('batch').split('\n')
        for host in multi_hosts:
            if host == '':
                break
            sn, hostname, eth1, eth2, idc, projects, cabinet, height = host.split()
            idc = get_object_or_404(IDC, name=idc)
            project_objs = []
            for s in ast.literal_eval(projects):
                project_objs.append(get_object_or_404(Project, service_name=s))
            if Server.objects.filter(eth1=eth1):
                emg = u'添加失败, 该IP%s已存在' % eth1
                return my_render('assets/host_add_batch.html', locals(), request)

            asset = Server(sn=sn,hostname=hostname,eth1=eth1,eth2=eth2,idc=idc,cabinet=cabinet,height=height)
            asset.save()
            asset.service = project_objs
            asset.save()

        smg = u'批量添加成功.'
        return my_render('assets/host_add_batch.html', locals(), request)

    return my_render('assets/host_add_batch.html', locals(), request)
