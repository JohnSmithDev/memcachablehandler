"""
Enhanced webapp.RequestHandler class(es)/decorator

Two advantages over webapp.RequestHandler
- Explcitly log (debug level) how long the request took.
  This is in the existing GAE logging, but this is more
  explicit/readable IMHO.
- Content for a URL can be memcached to (hopefully) speed
  up responses.  Obviously you'd have to be careful on something
  that uses cookies.

It's possible that this is an unnecessary optimization in many
cases, but it's easy enough to swap in/out.

An alternative take on this sort of problem can be found at
http://appengine-cookbook.appspot.com/recipe/webapp-page-caching-handler/
I've not tried it personally (I wasn't aware of its existence
until this was mostly finished.

Written by John Smith      | http://john-smith.appspot.com
Copyright Menboku Ltd 2010 | http://www.menboku.co.uk
Licenced under GPL v2      | http://www.gnu.org/licenses/gpl-2.0.html

"""

__author__ = "John Smith - http://john-smith.appspot.com"

import logging
import time
import datetime

from google.appengine.api import memcache
from google.appengine.ext import webapp

# Some settings/functions from my blog code, with reasonable
# defaults if they can't be found.
try:
    import blog_settings
    _USE_MEMCACHE_ = blog_settings.USE_MEMCACHE
except Exception, e:
    _USE_MEMCACHE_ = True

try:
    from cachability import can_use_cached_copy
except Exception, e:
    def can_use_cached_copy(*dontcare):
        pass
try:
    from offline import enqueue_log_task
except Exception, e:
    def enqueue_log_task(*dontcare):
        pass

# How long to keep memcached copy for (in seconds)
_CACHE_LIFE_ = 3600

# If returning a memcached copy, should an external cache also cache it?
_ENABLE_CACHE_CONTROL_ = True


class LoggingHandler(webapp.RequestHandler):
    """More explicit duration logging than webapp.RequestHandler"""

    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.init_time = time.time()

    def __del__(self):
        logging.debug("Handler for %s took %.2f seconds" %
                      (self.request.url, time.time() - self.init_time))


class HeadersAndContent:
    """Memcachable structure for storing/returning responses"""

    def __init__(self, headers=None, content=None, status_code=200,
                 analytics_tag=None):
        if headers:
            self.headers  = headers
        else:
            self.headers = []
        self.content = content
        self.status_code = status_code
        self.creation_date = datetime.datetime.now()
        self.analytics_tag = analytics_tag

    def respond(self, rh):
        for hdr in self.headers:
            rh.response.headers[hdr] = self.headers[hdr]
        rh.response.headers["X-Memcached-From"] = str(self.creation_date)
        if _ENABLE_CACHE_CONTROL_:
            rh.response.headers["Cache-Control"] = \
                "max-age=%d, public" % (_CACHE_LIFE_)
        head = False
        rh.response.out.write(self.content)
        if self.status_code != 200:
            rh.error(self.status_code)
        if self.analytics_tag:
            enqueue_log_task(rh, pagename=self.analytics_tag, 
                             from_memcache=True)


def memcachable(warh_method):
    """Decorator to add memcaching to webapp.RequestHandler methods

    In the decorated methods, you need to return the content, ideally
    as a HeadersAndContent, but a string will do.  Otherwise there
    won't be anything to memcache.

    """
    def innerfunc(self, *args):
        self.responded = False
        data = memcache.get(self.request.url)
        if _USE_MEMCACHE_ and can_use_cached_copy(self) and data:
            data.respond(self)
            self.responded = True
            logging.debug("Responded with memcached data for %s" %
                          (self.request.url))
            return True
        else:
            method_args = [self]
            method_args.extend(args)
            retval = warh_method(*method_args)
            if can_use_cached_copy(self):
                if _USE_MEMCACHE_ and retval:
                    if isinstance(retval, HeadersAndContent):
                        memcache.set(self.request.url, 
                                     retval,
                                     time=_CACHE_LIFE_)
                    else:
                        # Assume just the content; no headers,
                        # HTTP status, etc
                        memcache.set(self.request.url,
                                     HeadersAndContent(content=retval),
                                     time=_CACHE_LIFE_)
                else:
                    logging.warning("Memcache disabled and/or no value "
                                    "returned from handler for '%s'" % 
                                    (self.request.url))

            return True

    return innerfunc


class MemcachablePageHandler(LoggingHandler):
    """
    Much of this class became defunct in favour of @memcachable, but
    it's still worth using if only for the HEAD handler.

    The signatures for .head() and .get() methods have *dontcare just
    in case the 'real' handlers catch part of the URL as args via
    a regexp.  They are irrelevant here as we look at the full URL

    """
    
    def __init__(self):
        LoggingHandler.__init__(self)

    def cache_response(self, content, time=_CACHE_LIFE_):
        if content and len(content)>0 and can_use_cached_copy(self):
            logging.debug("Caching %d bytes of content for %s" % 
                          (len(content), self.request.url))
            memcache.set(self.request.url, content, time=time)
        else:
            logging.debug("NOT caching content for %s" %
                          (self.request.url))

    def head(self, *dontcare):
        """Basic handler to minimize spurious errors on dashboard"""
        if _USE_MEMCACHE_:
            data = memcache.get(self.request.url)
            if data:
                data.respond(self)
        # Don't bother serving/generating a "proper" page if
        # we don't have one cached - it's only HEAD after all

    def get(self, *dontcare):
        """
        Respond to request from memcache where available

        The inheriting class should do the following in
        its get() method:
        1. After calling this, check self.responded and
           return if it is True
        2. Call cache_response() with the rendered content.
           (NB the content would still have to be returned
           to the client)
        If you use the @memcachable decorator you get this (and
        more for free), you just need to return the content -
        ideally as a HeadersAndContent, but a string will
        be accepted.

        """
        self.responded = False
        if not can_use_cached_copy(self):
            return
        if _USE_MEMCACHE_:
            data = memcache.get(self.request.url)
            if data:
                data.respond(self)
                self.responded = True
                logging.debug("Responded with memcached page for %s" %
                              (self.request.url))
