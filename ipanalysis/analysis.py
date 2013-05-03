#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import re
import os
import sys
import csv
import socket
import urllib

import pygeoip

DEBUG = False
#DEBUG = True

ipRex = '((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'

def get_files(dirname):
    for root, dirs, files in os.walk(dirname):
        print root
    return files

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
    items = csvreader('country_continent.csv')

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

    print
    print "The %  for US, JP, AU "
    couns = {'US':0, 'JP':0, 'AU':0, 'EU':0}

    out = open('output.csv','r')
    tmp = False
    if not out.read():
        tmp = True
        out.close()
    out = open('output.csv','a')
    if tmp:
        out.write('date,partern,US,JP,AU,EU\n')

    for p in part_ip_country:
        couns = {'US':0, 'JP':0, 'AU':0, 'EU':0}
        #print "====================="
        #print "==\t  %s \t   ==" %p
        #print "====================="
        num = 0
        for a in part_ip_country[p]:
            plen = len(part_ip_country[p][a])
            num += plen

        for c in part_ip_country[p].keys():
            if couns.get(c, 'tmp') != 'tmp':
                couns[c] += len(part_ip_country[p][c])
                if DEBUG: print 'First',c
            else:
                region = items.get(c)
                if DEBUG: print c, 'in Continent',region
                if couns.get(region, 'tmp') != 'tmp':
                    couns[region] += len(part_ip_country[p][c])
                    if DEBUG: print 'Second',region

        if DEBUG: print couns
        for c in couns.keys():
            per = float(couns[c])/num *100
            float_per = "%.2f" % per
            #print "%s\t:" %c,"{0:.2%}".format(per),"\t"
            couns[c] = float_per 
        print

        hour = logfile.split('.')[1]
        #line = hour + ','+p+','+ "%.2f" %couns['US']+ ','  + "%.2f" %couns['JP'] + ',' + "%.2f" %couns['AU'] +'\n'
        line = hour + ','+p+','+ couns['US']+ '%,'+couns['JP'] +'%,'+couns['AU']+'%,'+couns['EU'] +'%\n'
        out.write(line)
    out.close()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-f", "--filename", help="The name of file", dest="filename")
    (options, args) = parser.parse_args()
    if not options.filename:
        print "Please check the input"
        sys.exit(1)

    if not os.path.exists(options.filename):
        files = get_files('.')
        import fnmatch
        logfiles = fnmatch.filter(files, "%s*" % options.filename)
        if not len(logfiles):
            print "Please check the file exists!"
            sys.exit(1)
        else:
            for filename in logfiles:
                print "Handling the %s" % filename
                main(filename)
    else:
        print "Handling the %s" % options.filename
        main(options.filename)
