#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import os
import re

import time
import datetime
import bporemote

def filelist(ossobj):
    '''
    INPUT: oss://xxxx/xxxx/xxx
    OUTPUT: [ 'dddd-dd-dd dd:dd  dMB oss://xxxx/xxxx/xxx', 'dddd-dd-dd dd:dd  dKB oss://xxxx/xxxx/xxx' ]
    '''
    lines = []
    match = re.compile('(^[\d].*) \n')
    cmd = 'osscmd ls %s' % ossobj
    stdin, stdout, stderr = os.popen3(cmd)
    output = stdout.readlines()
    for line in output:
        m = match.findall(line)
        if m: lines.append(m[0])
    return lines

def hourlist(daytime):
    '''
    INPUT: a datetime.datetime object
    OUTPUT: a list has hours before the input
    '''
    hours = []
    prefix = daytime.strftime('%Y%m%d')
    now_hour = daytime.hour
    for x in xrange(0, now_hour):
        hours.append("%02d" %x)
    hours.append("%02d" %now_hour)

    return [ prefix + h for h in hours ]

def cmplist(alist, blist):
    outlist = set(alist) - set(blist)
    return list(outlist)

def checkoss(hours):
    YYYYMMDD = now.strftime('%Y/%m/%d/') )
    ossobj = os.path.join( 'oss://', YYYYMMDD)
    lines = filelist(ossobj)
    m = re.compile('(\d{10})')
    hours_lines = [ m.findall(x)[0] for x in lines ]
    
    missing = cmplist(hours, hours_lines)
    if missing:
        print "Missing files: {}".format(missing)

    return missing

def checkhost(host, cmd, hours):
    remote = bporemote.Remote()
    remote.add_host(host)
    result = remote.run_once(cmd) 
    filelist = result['stdout']
    m = re.compile('.*\.(\d{10})\.log\n')
    file_hour = m.findall(filelist[0])

    missing = cmplist(hours, file_hour)
    if missing:
        print "Missing files: {}".format(missing)

    return missing

def main():
    from config import *
    now = datetime.datetime.now()
    hours = hourlist(now)

    checkcmd = 'ls ' + os.path.join(dirname, now.strftime('%Y%m%d'))

    oss_missing = checkoss(hours)
    host_missing = checkhost(target, checkcmd, hours)
    if oss_missing:
        remote_source = bporemote.Remote()
        remote_source.add_host(source)
        remote_target= bporemote.Remote()
        remote_target.add_host(target)

        for h in oss_missing:
            f = "%s.%s.log" %(prefix, h)
            sfile = os.path.join(dirname, h[:8], f)
            ossfile = os.path.join(oss_pre, h[:4], h[4:6], h[6:8], f+'.gz')
            try:
                cmd = 'gzip -f %s' % sfile
                remote_source.run(cmd)
            except:
                pass
            cmd = 'osscmd put %s  %s' %(sfile+'.gz', ossfile)
            remote_source.run(cmd)

            cmd = 'osscmd get %s %s' %(ossfile, sfile+'.gz')
            remote_target(cmd)
            cmd = 'gunzip -f %s' % sfile
            remote_target(cmd)

        remote_source.close()
        remote_target.close()

    if host_missing:
        remote_target= bporemote.Remote()
        remote_target.add_host(target)
        for h in host_missing:
            f = "%s.%s.log" %(prefix, h)
            sfile = os.path.join(dirname, h[:8], f)
            ossfile = os.path.join(oss_pre, h[:4], h[4:6], h[6:8], f+'.gz')
            cmd = 'osscmd get %s %s' %(ossfile, sfile+'.gz')
            remote_target(cmd)
            cmd = 'gunzip -f %s' % sfile
            remote_target(cmd)
        remote_target.close()

    if host_missing:
        reason = '@target host: missing {}'.format(host_missing)
        bpomail.sendMail(smtp_server, smtp_user, smtp_pass, from_email, to_email, subject, reason)
    if oss_missing:
        reason = '@source host: missing {}'.format(host_missing)
        bpomail.sendMail(smtp_server, smtp_user, smtp_pass, from_email, to_email, subject, reason)


if __name__ == '__main__':
    main()
