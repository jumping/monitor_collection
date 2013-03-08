#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import csv

class AttributeDict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class Parse(object):
    def __init__(self, csvfile):
        self.csvfile = csvfile
        self.fieldnames = ['url', 'timeout','match','length','mail_addresses']

    def skip(self, num =1):
        """skip some lines from head"""
        self.fileobj = open(self.csvfile, 'rb')
        while num > 0:
            tmp = self.fileobj.readline()
            num -= 1

    def content(self):
        urls = []
        dictreader = csv.DictReader(self.fileobj, self.fieldnames, delimiter =';',quotechar = '"')
        for row in dictreader:
            notice_to = row['mail_addresses'].split(',')
            row['mail_addresses'] = notice_to
            urls.append(row)
        return urls

def main():
    '''
    '''
    parse = Parse('urls.csv')
    parse.skip()
    urls = parse.content()
    print urls

if __name__ == '__main__':
    main()

