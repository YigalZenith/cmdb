#!/bin/env python2.7
# coding=utf8

# Import python libs
import json
import MySQLdb

# Import salt modules
import salt.config
import salt.utils.event


__opts__ = salt.config.client_config('/etc/salt/master')

# Create MySQL connect
conn = MySQLdb.connect(host='192.168.0.56', user='django', passwd='Admin123', db='cmdb', port=3306)
cursor = conn.cursor()

# Listen Salt Master Event System
event = salt.utils.event.MasterEvent(__opts__['sock_dir'])
for eachevent in event.iter_events(full=True):
    ret = eachevent['data']
    if "salt/job/" in eachevent['tag']:
        # Return Event
        if ret.has_key('id') and ret.has_key('return') and 'find_job' not in ret['fun']:
            try:
                sql = '''INSERT INTO `salt_result`
                    (`fun`, `jid`, `result`, `host`, `success`, `full_ret` )
                    VALUES ( %s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (ret['fun'], ret['jid'],json.dumps(ret['return']), ret['id'],ret['success'], json.dumps(ret['fun_args'])))
                cursor.execute("COMMIT")
            except Exception,e:
                print e.message
        print ret
    # Other Event
    else:
        pass

