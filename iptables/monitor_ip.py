#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
#
# Monitor public ipaddress of no public ipaddress instance on grandcloud
#
# The whatismyip.com suggests to query interval must longer than 5 minutes. So please take care of it.
#
import re
import os
import urllib2
import pickle
import datetime
import random

import smtplib 
import email.Message

def email_alert(message):
    import config
    fromaddr = config.fromaddr
    toaddrs = config.toaddrs
    msg = email.Message.Message()
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    msg['Subject'] = 'Zhuamob Script Server IP Address affairs'
    msg.set_payload(message)
    server = smtplib.SMTP(config.smtp_server)
    #server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(fromaddr, toaddrs, str(msg))
    server.quit()

def public_ip():
    hosts = """http://automation.whatismyip.com/n09230945.asp
    http://adresseip.com
    http://www.aboutmyip.com/
    http://www.ipchicken.com/
    http://www.showmyip.com/
    http://monip.net/
    http://checkrealip.com/
    http://ipcheck.rehbein.net/
    http://checkmyip.com/
    http://www.raffar.com/checkip/
    http://www.thisip.org/
    http://www.lawrencegoetz.com/programs/ipinfo/
    http://www.mantacore.se/whoami/
    http://www.edpsciences.org/htbin/ipaddress
    http://mwburden.com/cgi-bin/getipaddr
    http://checkipaddress.com/
    http://www.glowhost.com/support/your.ip.php
    http://www.tanziars.com/
    http://www.naumann-net.org/
    http://www.godwiz.com/
    http://checkip.eurodyndns.org/""".strip().split("\n")

    ip_regex = re.compile("(([0-9]{1,3}\.){3}[0-9]{1,3})")
    req_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'}

    for i in range(3):
        SITEURL = random.choice(hosts)
        try:
            request = urllib2.Request(url=SITEURL, headers=req_headers)
            opener = urllib2.build_opener()
            response = opener.open(request)
            results = ip_regex.findall(response.read(200000))
            if results: return results[0][0]
            #if  response.code == 200 :
            #    content = response.read()
            #    return content.strip()
            #else:
            #    return
        except:
            pass
    return None

def load_old_results(file_path):
    '''Attempts to load most recent results'''
    pickledata = {}
    if os.path.isfile(file_path):
        picklefile = open(file_path, 'rb')
        pickledata = pickle.load(picklefile)
        picklefile.close()
    return pickledata

def store_results(file_path, data):
    '''Pickles results to compare on next run'''
    output = open(file_path, 'wb')
    pickle.dump(data, output)
    output.close()

def main():
    '''
    '''
    now = datetime.datetime.now().isoformat()
    pickle_file = '/tmp/data.pkl'
    if os.path.exists(pickle_file):
        first = False
    else:
        first = True
    pickledata = load_old_results(pickle_file)
    ipaddress = public_ip()
    if ipaddress:
        if ipaddress not in pickledata:
            pickledata[ipaddress] = str(now)
            store_results(pickle_file, pickledata)
            if first:
                print "First run this script, ip is %s." % ipaddress
            else:
                email_alert('IP Changed: %s @%s' % (ipaddress, now))
        else:
            print "NO Changed. @ %s" % (str(now))
    else:
        email_alert('Couldn\'t get ipaddress. @%s' %now)
        
if __name__ == '__main__':
    #print "Please notice: This run interval of script should not be shorter than 5 minutes."
    main()
