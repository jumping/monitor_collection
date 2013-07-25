#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import boto
import boto.ec2

def add_rule(security_group, start, end, ip):
    security_group.authorize(ip_protocol='tcp', from_port=start, to_port=end, cidr_ip=ip)


def main(ip, group_name, region, port):
    '''
    '''
    #group_name = 'Shanghai Office'
    #conn = boto.ec2.connect_to_region('ap-southeast-1')
    #conn = boto.ec2.connect_to_region('us-east-1')
    conn = boto.ec2.connect_to_region(region)
    security_group = conn.get_all_security_groups(group_name)
    if len(security_group) == 1:
        security_group = security_group[0]
    for ipaddress in ip:
        print "Item : %s" %ipaddress

        #### httpd
        if port == 1:
            add_rule(security_group, '80', '80', ipaddress)

        ####salt
        elif port == 2:
            add_rule(security_group, '4505', '4506', ipaddress)

        ####Ftp
        else:
            add_rule(security_group, '20', '21', ipaddress)
            add_rule(security_group, '1024', '65535', ipaddress)
    print "Done"


if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-i", "--ip", help="ip address", dest="ip", action="append")
    parser.add_option("-g", "--group", help="group", dest="group",default=None)
    parser.add_option("-r", "--region", help="region", dest="region",default="us-east-1")
    parser.add_option("-p", "--port", dest="port", help="port: \n 1. http(80); 2. salt(4505-4506) 3. ftp(20-21,1024-65535) \n", default=1)

    (options, args) = parser.parse_args()
    if not options.group:
        print "Please input group name"
        sys.exit(0)

    port = options.port

    ip = options.ip
    for i in ip:
        if ',' in i:
            ip.remove(i)
            ip.extend(i.split(','))
    for i in ip:
        print i
        if not '/' in i:
            ip.remove(i)
            i = i+'/32'
            ip.append(i)
    print "Adding {0} ...".format(ip)
    main(ip, options.group, options.region, port)
    #main(ip)

