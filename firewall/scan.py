#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import os
import Queue
import logging
import datetime
import threading

import bporemote
import rule

def output(dictname, loghd):
    loghd.warning('###################')
    for k in dictname.keys():
        loghd.warning('%s :' % k)
        loghd.warning('%s' % dictname[k])
    loghd.warning('#######END#########')

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
            self.out_queue.put(host+"HH"+(result['stdout'][0]))
            self.queue.task_done()

    def _stop(self):
        if self.isAlive():
            Thread._Thread__stop(self)

class ThreadCompare(threading.Thread):
    '''
    compare  current rules with saved rules
    '''
    def __init__(self, out_queue, logger):
        threading.Thread.__init__(self)
        self.out_queue = out_queue
        self.logger = logger

    def run(self):
        while True:
            current = self.out_queue.get()
            host, rules = current.split("HH")
            #compare current rules and saved rules
            saved_parse = rule.Parse(os.path.join('saved',host))
            curre_parse = rule.Parse(rules)
            header_compare = rule.DictDiffer(saved_parse.header, curre_parse.header)
            body_compare   = rule.Compare(saved_parse.body, curre_parse.body)

            header_sum = header_compare.summary()
            body_sum = body_compare.summary()
            if header_sum: output(header_sum, self.logger)
            if body_sum:   output(body_sum, self.logger)

            self.out_queue.task_done()


class ThreadSave(threading.Thread):
    '''
    save rules
    '''
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while True:
            current = self.out_queue.get()
            host, rules = current.split("HH")
            #save rules as example
            if not os.path.exists('saved'): os.mkdir('saved')
            fobj = open(os.path.join('saved', host), 'w')
            for rule in rules.split('\n'):
                fobj.write(rule+'\n')
            fobj.close()
            self.out_queue.task_done()

    def _stop(self):
        if self.isAlive():
            Thread._Thread__stop(self)

def main(ip, first=False):
    '''
    '''
    timeout = 30
    logger = logging.getLogger()
    hdlr = logging.FileHandler('log.txt')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    logger.info('Starting at %s' % datetime.datetime.now())
    if first: logger.info('Run initialization process')
    assert isinstance(ip, list)

    #queue
    queue = Queue.Queue()
    out_queue = Queue.Queue()
    
    #get data
    for h in ip:
        queue.put(h)

    #threading spool 
    for i in range(5):
        t = ThreadFetch(queue, out_queue)
        t.setDaemon(True)
        t.start()

    if first:
        #threading spool
        for i in range(5):
            t = ThreadSave(out_queue)
            t.setDaemon(True)
            t.start()

    else:
        #threading spool
        for i in range(5):
            t = ThreadCompare(out_queue, logger)
            t.setDaemon(True)
            t.start()

    queue.join()
    out_queue.join()

    logger.info('End at %s' % datetime.datetime.now())


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
