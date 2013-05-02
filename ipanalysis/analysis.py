#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import re
import os
import csv
import socket
import urllib

import pygeoip

DEBUG = False
#DEBUG = True

ipRex = '((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'

def partern(line):
    match = re.compile('.*\?ptr=(.*)$')
    match2 = re.compile('(.*)-.*$')
    unquote = urllib.unquote(line).split('&')
    compaign = unquote[0]
    matched = match.findall(compaign)
    if matched:
        fmatched = matched[0]
        matched2 = match2.findall(fmatched)
        if matched2:
            return matched2[0]
        else:
            return matched[0]
    else:
        if DEBUG: print 'aaaaaaaaaaaa'
        return 


def iptime(filename):
    filt_words = ['bot', 'spider']
    ip_times = []
    fileobj = open(filename, 'r')
    lines = fileobj.readlines()
    print "The nubmer of the all line is: %d" %len(lines)
    fileobj.close()
    for line in lines:
        l = line.split('\t')
        p = partern(l[5])
        if not p: 
            if 'bot' not in line or 'spider' not in line:
                if DEBUG: print line
            continue
        ip_times.append((l[0],l[2],p))
    return ip_times

def query(ip):
    '''
    return the country of the ip
    '''
    gi4 = pygeoip.GeoIP('GeoIP.dat', pygeoip.MEMORY_CACHE)
    try:
        country = gi4.country_code_by_addr(ip)
        return country
    except socket.error, msg:
        if DEBUG: 
            print ip, msg
            return 
        else:
            pass

def csvreader(filename):
    items = {}
    data = csv.reader(open(filename))
    fields = data.next()
    for row in data:
        items[row[0]] = row[1]
    return items

def main(logfile):
    '''
    '''
    wrongip = 0

    if not os.path.exists('GeoIP.dat'):
        import subprocess
        cmd = 'wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz && gunzip GeoIP.dat.gz'
        retcode = subprocess.call(cmd)
        if retcode != 0:
            print "Please check the GeoIP.dat, or download yourself."
            import sys
            sys.exit(1)

    ip_time_part = iptime(logfile)
    part_ip_country = {}
    for item in ip_time_part:
        ip, time, part = item

        tmp =  re.findall(re.compile(ipRex),ip)
        if not tmp:
            if DEBUG: 
                print "Wrong IP: %s" %ip
            wrongip += 1
            continue

        country = query(ip)
        if not country and DEBUG: 
            print ip, item

        if not part_ip_country.get(part, None):
            part_ip_country[part] = {}

        if not part_ip_country[part].get(country, None):
            part_ip_country[part][country] = []

        part_ip_country[part][country].append(ip)

    if DEBUG:
        total = 0
        for p in part_ip_country:
            print "      Partern  %s   " %p
            for c in part_ip_country[p]:
                length = len(part_ip_country[p][c])
                total += length
                print c,length
        print "Total useful IP : %d" % total
        print "Total Wrong IP : %d" % wrongip

    print "The %  for US, JP, AU "
    couns = ['US', 'JP', 'AU']
    for p in part_ip_country:
        print
        print "\t  %s \t " %p
        print
        num = 0
        for a in part_ip_country[p]:
            plen = len(part_ip_country[p][a])
            num += plen

        for c in couns:
            try:
                pc = len(part_ip_country[p][c])
                per = float(pc)/num
                print "%s \t :" %c,"{0:.2%}".format(per),"\t"
            except:
                print "%s \t :" %c,"{0:.2%}".format(0.0),"\t"


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-n", "--name", help="The name of file", dest="filename")
    (options, args) = parser.parse_args()
    if not options.filename:
        print "Please check the input"
        sys.exit(1)

    if not os.path.exists(options.filename):
        print "Please check the file exists!"
        sys.exit(1)

    main(options.filename)


