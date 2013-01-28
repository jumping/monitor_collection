#!/bin/env python

import random
import datetime
import sys
import os


sys.path.append('/mnt/apps/ec2/scripts/auto_scaling')
sys.path.append('/mnt/apps/ec2/scripts/bposols')

import scan
import remote

now = datetime.datetime.now().strftime('%Y-%m-%d %T')
log = '/mnt/tmp/monitor/history.txt'
print now

sst = [ '10.252.7.0', '10.85.150.57' ]
#sst = [ '10.252.7.0', '10.85.150.57', '10.252.75.209', '10.253.194.162' ]
rahost = random.sample(sst, 1)
#rahost = random.choice(sst)
#print rahost
#'10.85.150.57'

#cmd = "/bin/sed -i '5 c\%s  sstracker.bposervers.com' /etc/hosts" %rahost[0]
cmd = "/bin/sed -i '4 a\%s  sstracker.bposervers.com' /etc/hosts" %rahost[0]
print cmd

#read lines from the history.txt
f = open(log)
lines = f.readlines()
lines = [ line.strip() for line in lines ]
f.close()

#check autoscaling group for getting ip address of running instances 
ips = scan.running_ip()
print ips

runs = list(set(ips) - set(lines))

if runs:
    remote_host = remote.Remote()
    for run in runs:
        remote_host.add_host(run)
        remote_host.run_once(cmd)
    remote_host.close()

    #write back the ips to history.txt file
    f = open(log, 'w')
    for ip in ips:
        f.write(ip)
        f.write('\n')
    f.close()
else:
    print "No new instances!"
