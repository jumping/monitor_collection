#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import re
import urllib2

class Check(object):
    def __init__(self, url):
        self.url = url

    def getinfo(self, default_timeout=0.5):
        response = urllib2.urlopen(url=self.url, timeout=default_timeout)
        #urllib2.URLError: <urlopen error timed out>
        self.headers = response.info()
        self.content = response.read()

    def length(self):
        return self.headers.get('content-length',0)

    def header(self, target):
        TARGET = re.compile(target)
        result = TARGET.match(self.content[:50])
        if result: 
            return result.pos
        else:
            return None

def main(url, keyword):
    '''
    '''
    check = Check(url)
    check.getinfo(2)
    print check.length()
    print check.header(keyword)

if __name__ == '__main__':
    url = 'http://www.baidu.com'
    keyword = 'STATUS OK'
    main(url, keyword)

