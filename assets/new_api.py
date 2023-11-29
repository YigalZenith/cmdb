# coding:utf-8
import urllib
import urllib2
import json
import ssl
from models import ENVIRONMENT,Project,Server


from IPy import IP
from django.core.paginator import Paginator, EmptyPage, InvalidPage


def page_list_return(total, current=1):
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page+1)


def pages(posts, r):
    """分页公用函数"""
    contact_list = posts
    p = paginator = Paginator(contact_list, 10)
    try:
        current_page = int(r.GET.get('page', '1'))
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(p.page_range), current_page)

    try:
        contacts = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0
    if current_page <= (len(p.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    return contact_list, p, contacts, page_range, current_page, show_first, show_end


def sort_ip_list(ip_list):
    """ ip地址排序 """
    ip_list.sort(key=lambda s: map(int, s.split('.')))
    return ip_list


def sort_ipaddr(hosts):
    # 查询到的结果去重并转换成列表
    servers = list(set(hosts))
    # ip和对象字典
    servers_dic = {}
    # ip列表
    servers_lis = []
    for server in servers:
        if server.eth1:
            servers_dic[server.eth1] = server
            servers_lis.append(server.eth1)
        elif host.eth2:
            servers_dic[host.eth2] = host
            servers_lis.append(host.eth2)

    # 对ip列表排序
    sort_ip_list(servers_lis)
    # 对象列表排序
    servers = []
    for eth1 in servers_lis:
        servers.append(servers_dic[eth1])
    return servers


def get_mask_ip(mask):
    """ 得到一个网段所有ip """
    ips = IP(mask)
    ip_list = []
    for ip in ips:
        ip_list.append(str(ip))
    ip_list = ip_list[1:]
    return ip_list


def get_zdata(username):
    zdata = []

    env_list = [i[0] for i in ENVIRONMENT]
    project_list = Project.objects.all()
    server_list = Server.objects.all()

    for i in range(len(env_list)):
        env_id = (i+1)*10000
        zdata.append({"id": env_id, "pId": '-99', "name": env_list[i]})
        for j in range(len(project_list)):
                project_id = env_id+(j+1)*100
                server_count = Server.objects.filter(service=project_list[j]).filter(env=env_list[i]).count()
                Pro_name = "%s (%s) " % (project_list[j].service_name, server_count)
                zdata.append({"id": project_id, "pId": env_id, "name": Pro_name, "isParent": True})
                for k in range(len(server_list)):
                    server_id = project_id+k+1

                    related_project_list = server_list[k].service.all()
                    for m in related_project_list:
                        if server_list[k].env == env_list[i] and m.service_name == project_list[j].service_name:
                            if project_list[j].service_name == 'kvm':
                                vm_count = Server.objects.filter(vm=server_list[k].uuid).count()
                                hostname = "%s--%s 【%s】" % (env_list[i], server_list[k].eth1, vm_count)
                            else:
                                hostname = "%s--%s" % (env_list[i], server_list[k].eth1)
                            zdata.append({"id": server_id, "pId": project_id, "name": hostname, "uuid": server_list[k].uuid, "icon": "/static/img/zTreeStyle/img/diy/linux-ico.png"})
    return zdata
