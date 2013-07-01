#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import re
import sys
import time
import boto

import bpomail

def monitor(conn, title, identifier=None):
    #events = conn.get_all_events(max_records=100)
    title = u'free storage capacity'
    events = conn.get_all_events()
    for event in events:
        print event.source_identifier,event.source_type,event.date,event.message
        if re.match(title, event.message):
            bpomail.simpleMail("%s: %s" %(title.upper(), event.source_identifier),event.message)
            return True
        

def main(title=None):
    '''
    '''
    if not title:
        title = u'free storage capacity'
    conn = boto.connect_rds()
    return monitor(conn, title)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-m", "--match", help="matched message", dest="match")
    parser.add_option("-w", "--watch", help="wait the message appear", dest="watch", action="store_true")

    (options, args) = parser.parse_args()
    if not options.match:
        main()
        sys.exit(0)
    else:
        title = options.match

    if options.watch:
        while not main(title):
            time.sleep(60)
            print "Try again."
