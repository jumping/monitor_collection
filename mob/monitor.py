#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import urllib2
import socket

import check
import parse
import bpomail
import config

DEBUG = config.debug

def alert(to_email, reason):
    smtp_server = config.smtp_server
    smtp_user   = config.smtp_user
    smtp_pass   = config.smtp_pass
    from_email  = config.from_email
    subject     = config.subject
    if not DEBUG:
        bpomail.sendMail(smtp_server, smtp_user, smtp_pass, from_email, to_email, subject, reason)

def monitor(csvfile):
    parser = parse.Parse(csvfile)
    parser.skip()
    urls = parser.content()
    for theurl in urls:
        u = parse.AttributeDict(theurl)
        if DEBUG:
            print "-------------"
            print  u.url
            print "-------------"
        checker = check.Check(u.url)
        try:
            checker.getinfo(float(u.timeout))
        #except urllib2.URLError as e:
        #    reason = 'timed out'
        #    if reason in e.reason:
        #        alert(u.mail_addresses, reason)
        #        if DEBUG: print reason
        #        continue
        except (urllib2.URLError, socket.timeout) as e:
            #reason = 'timed out'
            #if e == 'timeout' or reason in e.reason:
            #if e == 'timeout':
            #    alert(u.mail_addresses, reason)
            #    if DEBUG: print reason
            #    continue
            msg = '%s : %s' %(u.url,e)
            alert(u.mail_addresses, msg)
            if DEBUG: print msg
            continue


        leng = checker.length()
        if int(leng) < int(u.length):
            if DEBUG: print 'check point 1'
            reason = "Response Too short: %d" % int(leng)
            if DEBUG: print reason
            alert(u.mail_addresses, reason)
            continue

        searcher =  checker.header(u.match)
        if searcher and int(searcher) != 0:
            if DEBUG: print 'check point 2'
            reason = "Response Too short: %d" % int(leng)
            reason = "NO Found: %s" % u.match
            if DEBUG: print reason
            alert(u.mail_addresses, reason)
            continue

def main():
    '''
    '''
    import datetime
    print datetime.datetime.now()
    monitor('urls.csv')



if __name__ == '__main__':
    main()


