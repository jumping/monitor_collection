#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#

#step 1: scan all regions of AWS for public ipaddress set A
#step 2: scan all rules of iptables, get public ipaddress set C
#step 3: compare A and B(fixed ips) with existings C, save iptables then a. remove old; b. add new
#step 4: report : removed and added

import datetime
import subprocess

import boto

import config
#DEBUG = False
DEBUG = True

def get_eips(conn):
    '''
    scan allocated elastic ip  on a region
    '''
    ips = []
    if not conn:
        return
    eips = conn.get_all_addresses()
    if DEBUG and len(eips) > 0: print eips
    for eip in eips:
        ips.append(eip.public_ip)
    if DEBUG and ips: print ips
    return ips

def get_instance_ips(conn):
    '''
    scan all running instance then return all public ipaddress on a region
    '''
    ips = []
    if not conn:
        return
    reservations = conn.get_all_instances()
    if DEBUG and len(reservations): print reservations
    for reservation in reservations:
        for instance in reservation.instances:
            ips.append(instance.ip_address)
    if DEBUG and ips: print ips
    return ips

def ec2_region_ips(regioname=None):
    '''
    if no regioname, will scan all region
    '''
    ips = []
    regions = []
    if not regioname:
        conn = boto.connect_ec2()
        regs = conn.get_all_regions()
        for reg in regs:
            regions.append(reg.name)
    else:
        reg = boto.ec2.connect_to_region(regioname)
        regions.append(reg.name)
    for region in regions:
        print "Scanning %s" % region
        connection = boto.ec2.connect_to_region(region)
        eips = get_eips(connection)
        runs = get_instance_ips(connection)

        if eips:
            ips.extend(eips)
        if runs:
            ips.extend(runs)

    return filter(lambda x: x, ips)


def main():
    '''
    '''
    import os
    pathdir = os.getcwd()
    cmdfile = os.path.join(pathdir, 'change_iptables.pl')
    pickle_file = '/tmp/firewall.pkl'
    fixed = config.fixed

    deletelist, addlist = [], []

    ipa = ec2_region_ips()

    ipa.extend(fixed)
    print "==All Wanted=="
    print ipa
    print "=====End========"
    import monitor_ip as monitor
    pickledata = monitor.load_old_results(pickle_file)
    if pickledata:
        ipstored = pickledata['iplist']
        deletelist = list(set(ipstored) - set(ipa))
        addlist    = list(set(ipa) - set(ipstored))

    pickledata['iplist'] = ipa

    if deletelist:
        print "Deleting ..."
        if DEBUG: print deletelist
        else:
            for item in deletelist:
                cmd = "%s -d -ip %s" %(cmdfile, item)
                output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    if addlist:
        print "Adding ..."
        if DEBUG: print addlist
        else:
            for item in addlist:
                cmd = "%s -a -ip %s" %(cmdfile, item)
                output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    monitor.store_results(pickle_file, pickledata)


if __name__ == '__main__':
    main()
