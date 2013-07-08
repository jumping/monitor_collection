#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import sys
import os
import re
import subprocess

import time
import datetime
import bporemote
import bpomail

import config

#DEBUG = True
DEBUG = False

def filelist(ossobj):
    '''
    INPUT: oss://xxxx/xxxx/xxx
    OUTPUT: [ 'dddd-dd-dd dd:dd  dMB oss://xxxx/xxxx/xxx', 'dddd-dd-dd dd:dd  dKB oss://xxxx/xxxx/xxx' ]
    '''
    lines = []
    cmd = 'osscmd ls %s' % ossobj
    if DEBUG: print cmd
    match = re.compile('(^[\d].*) \n')
    #stdin, stdout, stderr = os.popen3(cmd)
    #output = stdout.readlines()
    d = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    output = d.stdout.readlines()
    if 'Error' in output:
        print "Please check the cmd or authoriztion."
        print output
        print cmd
        sys.exit(1)
    for line in output:
        m = match.findall(line)
        if m: lines.append(m[0])

    if DEBUG: print "@OSS: ", lines

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
    #hours.append("%02d" %now_hour)

    return [ prefix + h for h in hours ]

def cmplist(alist, blist):
    outlist = set(alist) - set(blist)
    return list(outlist)

def checkoss(hours, now):
    YYYYMMDD = now.strftime('%Y/%m/%d/') 
    ossobj = os.path.join( config.oss_pre, YYYYMMDD)
    lines = filelist(ossobj)
    m = re.compile('(\d{10})')
    hours_lines = [ m.findall(x)[0] for x in lines ]
    
    missing = cmplist(hours, hours_lines)
    if missing:
        print "Missing files: ", missing

    return missing

def checkhost(host, cmd, hours):
    remote = bporemote.Remote()
    try:
        remote.add_host(host)
        result = remote.run_once(cmd) 
    except Exception, e:
        print e
        return ''
    filelist = result['stdout']
    m = re.compile('.*\.(\d{10})\.log\n')
    if len(filelist) > 0:
        file_hour = m.findall(filelist[0])
    else:
        return ''

    missing = cmplist(hours, file_hour)
    if missing:
        print "Missing files: ", missing
    #print missing

    return missing

def main():
    now = datetime.datetime.now()
    hours = hourlist(now)

    checkcmd = 'ls ' + os.path.join(config.dirname, now.strftime('%Y%m%d'))

    oss_missing = checkoss(hours, now)
    host_missing = checkhost(config.target, checkcmd, hours)

    #check the oss_missing
    if oss_missing:
        print "@OSS, missing: ", oss_missing
    else:
        print "@OSS, No missing."

    #check the host_missing
    if isinstance(host_missing, str):
        print "Could not connect to the instance: %s !" % config.target
        sys.exit(0)

    elif host_missing:
        print "@source host, missing: ", host_missing, oss_missing
    else:
        print "@source host, NO missing."
        sys.exit(0)

    if oss_missing and not DEBUG:
        remote_source = bporemote.Remote()
        remote_source.add_host(config.source)
        remote_target= bporemote.Remote()
        remote_target.add_host(config.target)

        for h in oss_missing:
            f = "%s.%s.log" %(config.prefix, h)
            sfile = os.path.join(config.dirname, h[:8], f)
            ossfile = os.path.join(config.oss_pre, h[:4], h[4:6], h[6:8], f+'.gz')
            try:
                cmd = 'gzip -f %s' % sfile
                remote_source.run_once(cmd)
            except:
                pass
            cmd = 'osscmd put %s  %s' %(sfile+'.gz', ossfile)
            remote_source.run_once(cmd)

            cmd = 'osscmd get %s %s' %(ossfile, sfile+'.gz')
            remote_target.run_once(cmd)
            cmd = 'gunzip -f %s' % sfile
            remote_target.run_once(cmd)

        remote_source.close()
        remote_target.close()

    if host_missing and not DEBUG:
        remote_target= bporemote.Remote()
        remote_target.add_host(config.target)
        for h in host_missing:
            f = "%s.%s.log" %(config.prefix, h)
            sfile = os.path.join(config.dirname, h[:8], f)
            ossfile = os.path.join(config.oss_pre, h[:4], h[4:6], h[6:8], f+'.gz')
            cmd = 'osscmd get %s %s' %(ossfile, sfile+'.gz')
            remote_target.run_once(cmd)
            cmd = 'gunzip -f %s' % sfile
            remote_target.run_once(cmd)
        remote_target.close()

    if host_missing and not DEBUG:
        reason = '@target host: missing %s' %(','.join(host_missing))
        bpomail.sendMail(config.smtp_server, config.smtp_user, config.smtp_pass, config.from_email, config.to_email, config.subject, reason)
    if oss_missing and not DEBUG:
        reason = '@source host: missing %s' %(','.join(host_missing))
        bpomail.sendMail(config.smtp_server, config.smtp_user, config.smtp_pass, config.from_email, config.to_email, config.subject, reason)


if __name__ == '__main__':
    now = datetime.datetime.now()
    if int(now.minute) < 11:
        print "This script should run after the normal put and get process."
        sys.exit(0)
    main()
