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

    def header(self, target, size=200):
        source = self.content[:size]
        if isinstance(source, unicode):
            source = data.encode('utf-8')

        stripped_tags = re.sub(r'<![^>]*>', '',source)
        data = '\n'.join((l.rstrip() for l in stripped_tags.splitlines() if l.strip() != ''))

        TARGET = re.compile(target)
        result = TARGET.match(data)

        if result: 
            return result.pos
        else:
            print data
            return None

def main(url, keyword):
    '''
    '''
    check = Check(url)
    check.getinfo(2)
    print check.length()
    print check.header(keyword)

if __name__ == '__main__':
    #url = 'http://api.wall.zhuamob.com/OfferList?device_id=aaa&mac=xxx&app_id=1b7544a62ac1050aff63b90ee7f3402c'
    #keyword = """{"code":200,"""
    url = 'http://www.baidu.com'
    keyword = """html,body"""
    main(url, keyword)

