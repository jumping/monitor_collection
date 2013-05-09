#!/usr/bin/env python
# -*- coding: UTF8 -*-
# 
#   Jumping Qu @ BPO
#
#vim: ts=4 sts=4 et sw=4
#
import copy

class Parse(object):
    def __init__(self, filename):
        self.filename = filename
        self.header = []
        self.body = []
        self.tail = []
        self.read_file(self.filename)

    def read_file(self, f):
        '''
        read file and classify  content
        '''
        fobj = open(f)
        self.classify(fobj.readlines())
        fobj.close()

    def read_string(self, string):
        '''
        read string and classify  content
        '''
        self.classify(string)

    def classify(self, stream):
        '''
        classify the input to three parts
        '''
        for l in stream:
            if not l: continue
            if l.startswith('#') or l.startswith('*'):
                continue
            l = l.strip()

            if l.startswith(':'):
                self.header.append(l)
                continue

            if l.startswith('-A'):
                self.body.append(l)
                continue

            if l.startswith('COMMIT'):
                self.tail.append(l)
                continue


        
    def default_rule(self):
        '''
        normalize the default rule of chain
        '''
        tmp = {}
        for n in self.header:
            ns = n.lstrip(':').split(' ')
            if len(ns) == 3 and ns[1] in [ 'DROP', 'ACCEPT' ]:
                tmp[ns[0]] = ns[1]
        self.header = copy.deepcopy(tmp)
        
class Compare(object):
    def __init__(self, source, destin):
        self.source = source
        self.destin = destin
        self.find()

    def find(self):
        self.right = list(set(self.source) - set(self.destin))
        self.left  = list(set(self.destin) - set(self.source))


class DictDiffer(object):
    """
      From: http://code.activestate.com/recipes/576644-diff-two-dictionaries/
      Author: Hugh Brown 

      Calculate the difference between two dictionaries as:
      (1) items added
      (2) items removed
      (3) keys same in both but changed values
      (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


def main():
    '''
    '''

    print 'main'


if __name__ == '__main__':
    main()
