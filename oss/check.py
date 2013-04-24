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
    now = datetime.datetime.now()
    hours = hourlist(now)

    oss_missing = checkoss(hours)

