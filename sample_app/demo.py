#!/usr/bin/env python
"""
A simple demonstration GAE app for memcachablehandler

USAGE:
* Start up with dev_appserver  as you would any other GAE app
* View a page in your browser, put some random stuff in the
  url to get a new page.  Note the timestamp to indicate whether
  the page you are viewing is from memcache (or look for
  X-Memcached-From in the HTTP response headers)

Written by John Smith      | http://john-smith.appspot.com
Copyright Menboku Ltd 2010 | http://www.menboku.co.uk
Licenced under GPL v2      | http://www.gnu.org/licenses/gpl-2.0.html

"""

__author__ = "John Smith - http://john-smith.appspot.com"

import time
import datetime
import random
import re
import os
import sys
import logging

from google.appengine.ext import webapp
import wsgiref.handlers

from mchandler import MemcachablePageHandler, memcachable

class DemoPage(MemcachablePageHandler):
    # Note lack of .head() handler, but MemcachablePageHandler
    # will handle it, if there is memcached content

    @memcachable
    def get(self, extra_bit=None):
        # Some artificial latency to help make it more
        # obvious when the page is delivered from the cache
        time.sleep(random.randrange(5)+3)

        if extra_bit:
            sanitised = re.sub("\W", "", extra_bit)
        else:
            sanitised = "NoneSupplied"

        content = """<DOCTYPE html>
<html>
<head><title>Demo page for argument '%s'</title></head>
<body>
<h1>Demo page for '%s'</h1>
<p>Page generated at %s</p>
<p>Try these pages:
<ol>
<li><a href="/alpha">Alpha</a></li>
<li><a href="/beta">Beta</a></li>
<li><a href="/gamma">Gamma</a></li>
</ol>
</p>
</body>
</html>""" % (sanitised, sanitised, datetime.datetime.now())
        
        self.response.out.write(content)
        
        return content

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application=webapp.WSGIApplication(
        [
            ('/(.*)', DemoPage)
            ],
        debug = True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
