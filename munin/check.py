#!/usr/bin/env python26
# -*- coding: UTF8 -*-
#
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import os
import sys
import logging
import urllib2
import datetime
import BeautifulSoup
import gevent
from gevent.pool import Group

#1. download the homepage of munin
#2. pickup the url of every items
#3. check existence of images of every items

def fetch_gevent(url):
    """fetch url in the way of gevent"""
    try:
        result = urllib2.urlopen(url).read()
        return
    except urllib2.HTTPError as e:
        if e.code == 404:
            logging.info("Not Fund")
            return url
        else:
            logging.warn( "could not fetch the url %s" % url )
            return 'Error'

def fetch(url):
    if not url.startswith('http'):
        url = 'http://' + url

    logging.info(url)

    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError as e:
        if e.code == 404:
            logging.info("Not Fund")
            return
        else:
            logging.warn( "could not fetch the url %s" % url )
            return

def get(doc, flag, value):
    #INPUT: get(doc, 'ul', {'class':'groupview'})
    soup = doc.findAll(flag, value)
    return soup

def main(url):
    page = fetch(url)
    if not url.startswith('http'):
        url = 'http://' + url

    print url

    if not page:
        return

    soup = BeautifulSoup.BeautifulSoup(page)
    #get all hosts
    groupview = get(soup, 'ul', {'class':'groupview'})
    group = groupview[0]
    host = get(group, 'span', {'class': 'host'})
    host_url = []
    for h in host:
        host_url.append(h.contents[0].get('href'))

    print "There are {0} hosts.".format(len(host_url))

    group = Group()
    bad_img = []
    for hu in host_url:
        print "Checking on {0}".format(hu)
        host_page = fetch(os.path.join(url, hu))
        host_page_soup = BeautifulSoup.BeautifulSoup(host_page)
        imgs = get(host_page_soup, 'img', {'class':'i'})
        print "There are {0} urls.".format(len(imgs))

        img_url = [ os.path.join(url, img.get('src').replace('../','')) for img in imgs ]
        print "There are {0} urls will be checked.".format(len(img_url))
        fetch_result = group.map(fetch_gevent, img_url)
        fetch_result = filter(lambda x: x, fetch_result)
        bad_img.extend(fetch_result)

    if bad_img:
        print "The following images do not exits:"
    for bi in bad_img:
        print bi


if __name__ == '__main__':
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        print "Need a url!"
        sys.exit(0)

    start = datetime.datetime.now()
    main(url)
    end = datetime.datetime.now()
    print end - start
