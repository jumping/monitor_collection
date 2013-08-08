#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import time
import boto
import boto.ec2

def main(snapid):
    '''
    '''
    conn = boto.connect_ec2()
    snap = conn.get_all_snapshots([snapid])[0]
    while True:
        n = snap.progress
        if n != u'100%':
            time.sleep(10)
            n = snap.update()
            print n
        else:
            print snap.progress
            break

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

