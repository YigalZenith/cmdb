#coding:utf-8
from saltapi import SaltAPI
import ConfigParser,time,re


def saltstack():
    config = ConfigParser.ConfigParser()
    config.read("/data/cmdb/salt/config.ini")
    url = config.get("saltstack","url")
    user = config.get("saltstack","user")
    passwd = config.get("saltstack","pass")
    device = config.get("network","device")
    result_api = {'url':url,'user':user,'passwd':passwd,'device':device}
    return result_api


def update_command(host,project,war):
    ret_api = saltstack()
    sapi = SaltAPI(url=ret_api["url"],username=ret_api["user"],password=ret_api["passwd"])

    if project == 'cms':
        command1 = 'cd /srv/salt/%s/files; sh 2bak.sh' % project
        command2 = 'wget -q %s -P /srv/salt/%s/files/war/' % (war, project)
        command3 = 'md5sum /srv/salt/%s/files/war/*.war' % project
    else:
        command1 = 'cd /etc/puppet/modules/%s/files; sh 2bak.sh' %project
        command2 = 'wget -q %s -P /etc/puppet/modules/%s/files/war/' %(war,project)
        command3 = 'md5sum /etc/puppet/modules/%s/files/war/*.war' %project

    ret = sapi.remote_execution(host, 'cmd.run', command1)
    sapi.remote_execution(host, 'cmd.run', command2)
    ret2 = sapi.remote_execution(host, 'cmd.run', command3)
    # ret = sapi.remote_noarg_execution('openvpn','grains.items')
    return ret,ret2


def log_command(hostname,project):
    ret_api = saltstack()
    sapi = SaltAPI(url=ret_api["url"],username=ret_api["user"],password=ret_api["passwd"])
    T=time.strftime('%Y%m%d',time.localtime(time.time()))

    command1 = 'cat /ty/outlog/catalina%s.out | wc -l' % T
    linenum = sapi.remote_execution('%s' % hostname,'cmd.run' ,command1)

    if linenum > 10:
        command2 = 'tail -10 /ty/outlog/catalina%s.out' % T
    else:
        command2 = 'cat /ty/outlog/catalina%s.out' % T

    result1 = sapi.remote_execution('%s' % hostname,'cmd.run',command2)
    result1 = result1[0][hostname]
    linenum = linenum[0][hostname]
    return linenum,result1


"""
前端页面使用两个ajax时会用到
def get_endline_command(hostname,project,linenum):
    ret_api = saltstack()
    sapi = SaltAPI(url=ret_api["url"],username=ret_api["user"],password=ret_api["passwd"])
    T=time.strftime('%Y%m%d',time.localtime(time.time()))

    command0 = 'cat /ty/outlog/catalina%s.out | wc -l' % T
    endline = sapi.remote_execution('%s' % hostname,'cmd.run' ,command0)
    endline = int(endline[0][hostname])
    if endline:
        return endline
    else:
        return False
"""


def log_handle_command(hostname,project,linenum):
    ret_api = saltstack()
    sapi = SaltAPI(url=ret_api["url"],username=ret_api["user"],password=ret_api["passwd"])
    T=time.strftime('%Y%m%d',time.localtime(time.time()))
    linenum = int(linenum)

    command0 = 'cat /ty/outlog/catalina%s.out | wc -l' % T
    endline = sapi.remote_execution('%s' % hostname,'cmd.run',command0)
    endline = int(endline[0][hostname])

    if endline > linenum:
        command1 = "sed -n '%s,%sp' /ty/outlog/catalina%s.out " % (linenum+1,endline,T)
        result2 = sapi.remote_execution('%s' % hostname,'cmd.run',command1)
        result2 = result2[0][hostname]
        result2 = re.sub('\n', '<br>', result2)
    else:
        result2 = 'no update'
    return endline,result2


def online_command(hostname, project, command="puppet agent -t"):
    ret_api = saltstack()
    sapi = SaltAPI(url=ret_api["url"],username=ret_api["user"],password=ret_api["passwd"])
    if hostname == 'cms.tadu.com':
        command1 = "salt %s state.sls %s --output-diff --no-color --state-output=terse" % (hostname, project)
        hostname = 'saltmaster'
    else:
        command1 = command

    result = sapi.remote_execution(hostname, 'cmd.run', command1)
    result = result[0][hostname]
    return result,command1


def run_command(hostname, command="hostname"):
    ret_api = saltstack()
    sapi = SaltAPI(url=ret_api["url"], username=ret_api["user"], password=ret_api["passwd"])
    cmd = command.split()[0]
    auth_commands = ['hostname', 'ls', 'pwd', 'date', 'ip']
    if cmd in auth_commands:
        command1 = command
        result = sapi.remote_execution(hostname, 'cmd.run', command1)
        result = result[0][hostname]
    else:
        result = False
    return result
