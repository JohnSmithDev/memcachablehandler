memcachablehandler
==================

OVERVIEW
--------

A small library for Google App Engine to supplant the standard
webapp.RequestHandler with a version that will serve pages
from memcache where possible.  This should improve page response
times, and possibly reliability as well (in my personal experience,
memcache is much more reliable than the datastore on App Engine).

BASIC USAGE
-----------

There's a small sample application showing how the library can be
used, but in brief...

1. 'import mchandler' in .py files that have classes derived from
   webapp.RequestHandler
2. Change class definitions from webapp.RequestHandler to 
   mchandler.MemcachablePageHandler
3. get() methods should be preceded by a @mchandler.memcachable
   decorator
4. get() methods should return the rendered content so that it
   can be cached.  You could just return a string, but it's better
   to return a HeadersAndContent object, as this allows
   customizations of HTTP response headers etc

FURTHER NOTES
-------------

Changing webapp.RequestHandler to mchandler.MemcachablePageHandler
isn't strictly speaking necessary - you can put a decorator on the
former and it should still work.  The latter does give you a
head() handler, which is nice for reducing spurious errors in the
GAE dashboard shif you get robots doing HEAD requests.

If you don't want the content you generate to be cached, just
return None at the end of your handler.

mchandler.py will try to import a module cachability containing
the function can_use_cached_copy(), to determine if it is safe
to cache a page.  The default functionality is fairly basic, and
the file/function should be extended to cover whatever your
requirements are.  Of course, if you've got a handler that's
producing content that can't be cached most of the time, then
all of this is a bit of a waste of your time...

This code was originally part of my blogging system, and there
are calls to code that does some internal analytics type stuff
e.g. to ensure that pages that get served from the cache also
get logged.  This library should work fine without that (just calls
a dummy stub instead), and if you're using something like Google
Analytics you'll be fine.  (As I use the Ghostery Firefox
extension whilst browsing, it felt a bit hypocritical to put
Google Analytics on my own site :-)

There are a couple of settings you can tweak if desired, have
a look at the comments at the top of mchandler.py

BUGS
----

As of 2010/12/21 I'm not aware of any, but this code is still
pretty new and basic.

The main thing is that you need to be super-careful with what
gets cached and what doesn't.

ALTERNATIVES
------------

I haven't tried it personally, but this looks to cover similar ground:
http://appengine-cookbook.appspot.com/recipe/webapp-page-caching-handler/

CREDITS
-------

Written by John Smith December 2010
My blog (which uses this code): http://john-smith.appspot.com
My Twitter: John MMIX

LICENCE
-------
GPL v2 - http://www.gnu.org/licenses/gpl-2.0.html


