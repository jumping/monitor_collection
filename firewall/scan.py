#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import Queue
import threading

import bporemote
import rule


def read_host(fname):
    hosts = []
    fobj = open(fname)
    lines = fobj.readlines()
    fobj.close()
    for l in lines:
        if l.startswith('#') or not l: continue

        l = l.strip()
        host = l.split()[0]
        if host not in hosts: hosts.append(host)

    return hosts

class ThreadFetch(threading.Thread):
    '''
    Fetch firewall rules from remote host
    '''
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        cmd = '/sbin/iptables-save'
        while True:
            host = self.queue.get()
            remote = bporemote.Remote()
            remote.add_host(host)
            result = remote.run_once(cmd)

            if result['stderr'] != 0:
                result['stderr'].insert(0, host)
                self.out_queue.put("HH".join(result['stdout']))
            self.queue.task_done()

class ThreadCompare(threading.Thread):
    '''
    compare  current rules and save rules
    '''
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while True:
            current = self.out_queue.get()
            host, rules = current.split("HH")
            #compare current rules and saved rules
            self.out_queue.task_done()


def main(ip, first=False):
    '''
    '''
    assert isinstance(ip, list)

    #queue
    queue = Queue.Queue()
    out_queue = Queue.Queue()
    

    #threading spool 
    for i in range(5):
        t = ThreadFetch(queue, out_queue)
        t.setDaemon(True)
        t.start()

    #get data
    for h in ip:
        queue.put(host)

    #threading spool
    for i in range(5):
        t = ThreadCompare(out_queue)
        t.setDaemon(True)
        t.start()

    queue.join()
    out_queue.join()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-f", "--first", help="Will save the current rule as simple", dest="first",action='store_true')
    parser.add_option("-i", "--ip", help="the host ipaddress", dest="ip",action='store')
    (options, args) = parser.parse_args()

    first = True if options.first else False
    if options.ip:
        ip = options.ip.split(',')
    else:
        ip = read_host('host.txt')

    main(ip, first)
