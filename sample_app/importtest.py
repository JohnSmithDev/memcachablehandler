#!/usr/bin/env python

import sys

print("sys.path is %s" % sys.path)

sys.path.insert(0, "..") # so we can pull in mchandler
sys.path.insert(0, "/newproj/git/memcachablehandler")

print("sys.path is now %s" % sys.path)

import mchandler

# from mchandler import MemcachablePageHandler, memcachable

print("hello")

