#!/usr/bin/env python
# Jumping Qu - Jun 2012

import urllib
import httplib
import sys
import time
import urlparse

# config settings
POLLING_INTERVAL = 60  # secs
HOST = 'http://sstracker.bposervers.com'
URLS = (
        '%s/fp_ssite_tracking.php?ptr=TEST_UI&campaign=TEST_CAMPAIGN&sid=12345678901234567890123456789012&tt=test_typetag&sk=test&ka=test&page=1&ip=127.0.0.1&random=636&ref=&ua=Mozilla/5.0+TestBot&sl=10&random=11' % HOST,
    '%s/fp_out_tracking.php?ptr=TEST_UI&tt=test_typetag&sk=test&ka=test&ourl=&pos=2&sid=12345678901234567890123456789012&search=SS&sec=A&page=1&ip=127.0.0.1' % HOST,
    )

instance_id = urllib.urlopen('http://169.254.169.254/latest/meta-data/instance-id').readlines()[0]

def post(data):
    try:
        params = urllib.urlencode({'content':data})
        f=urllib.urlopen('http://insurancemoxie.appspot.com/sign',params)
        return True
    except:
        return False

class parse24(object):
    def __init__(self, parsed_url):
        self.scheme = parsed_url[0]
        self.netloc = parsed_url[1]
        self.path = parsed_url[2]
        self.query = parsed_url[4]

    def geturl(self):
        return "%s://%s%s?%s" % (self.scheme, self.netloc, self.path,
                self.query)

def timed_req(parsed_url):
    if parsed_url.scheme == 'https':
        conn = httplib.HTTPSConnection(parsed_url.netloc)
    else:
        conn = httplib.HTTPConnection(parsed_url.netloc)
    conn.set_debuglevel(0)
    start_timer = time.time()
    conn.request('GET', parsed_url.path)
    request_timer = time.time()
    resp = conn.getresponse()
    response_timer = time.time()
    content = resp.read()
    conn.close()
    transfer_timer = time.time()
    size = len(content)

    assert resp.status == 200, resp.reason

    # convert to offset millisecs
    request_time = (request_timer - start_timer) * 1000
    response_time = (response_timer - start_timer) * 1000
    transfer_time = (transfer_timer - start_timer) * 1000

    return (
        resp.status,
        resp.reason,
        size,
        request_time,
        response_time,
        transfer_time,
        )


def main():
    print 'id'.ljust(15),
    print 'time'.ljust(23),
    print 'request sent'.ljust(20),
    print 'response received'.ljust(20),
    print 'content transferred'.ljust(20),
    print 'size'.ljust(10),
    print 'status'
    
    print '------------'.ljust(15),
    print '------------------'.ljust(23),
    print '------------'.ljust(20),
    print '-----------------'.ljust(20),
    print '-------------------'.ljust(20),
    print '------'.ljust(10),
    print '------'.ljust(5)
    parsed_urls = [urlparse.urlparse(url) for url in URLS]
    while True:
        start = time.time()
        for parsed_url in parsed_urls:
            #should move to outside of this loop
            if sys.version_info[:2] == (2, 4):
                parsed_url = parse24(parsed_url)

            #title = '%s' % parsed_url.path.replace('/', '_')
            #print '--------------------------------'
            #print parsed_url.geturl()
            try:
                status,reason,size,request_time,response_time,transfer_time=timed_req(parsed_url)
                start_time = time.strftime('%D %H:%M:%S',time.localtime())
                print ('%s ' % instance_id).ljust(15),
                print '%s' % start_time.ljust(23),
                print ('%.0f ms ' % request_time).ljust(20),
                print ('%.0f ms ' % response_time).ljust(20),
                print ('%.0f ms ' % transfer_time).ljust(20),
                print ('%i ' % size).ljust(10),
                print ('%s ' % status).ljust(5),
                print '%s ' % parsed_url.geturl()

                times = (request_time, response_time, transfer_time)
                post('%s,%s,%.0f,%.0f,%.0f,%i,%s' %
                        (instance_id,start_time,request_time,response_time,transfer_time,size,status))
            except:
                print 'failed'
        elapsed = time.time() - start
        if POLLING_INTERVAL > elapsed:
            time.sleep(POLLING_INTERVAL - elapsed)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
