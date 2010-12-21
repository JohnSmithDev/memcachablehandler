"""
Determine if the response to a request can be cached.

Anything with personalizations or overrides should not be cached.

Written by John Smith      | http://john-smith.appspot.com
Copyright Menboku Ltd 2010 | http://www.menboku.co.uk
Licenced under GPL v2      | http://www.gnu.org/licenses/gpl-2.0.html

"""

__author = "John Smith - http://john-smith.appspot.com"

import logging

from google.appengine.api import users

### TO MAKE LIFE EASY, TRY TO LIST ALL COOKIES USED BY THE
### APP IN EITHER PERSONALIZATION_COOKIES OR GENERIC_COOKIES
### (And don't put something in both of them!)

# Any request containing these cookies should not have
# the response cached UNLESS the cookie value is in the value
# in the k/v pair
PERSONALIZATION_COOKIES = {
    "OverrideDeviceStyle": ["no"]
}

# These cookies don't affect cachability
GENERIC_COOKIES = []

def can_use_cached_copy(rh):
    """Return True/False if a cached response for this URL can be used"""

    # Maybe other HTTP methods can be cached, but they're
    # rare enough not to worry about
    if rh.request.method not in ["HEAD", "GET"]:
        return False

    # Maybe admin pages can be cachable, but better safe than sorry
    if users.is_current_user_admin():
        return False

    for cookie_key in rh.request.cookies:
        if cookie_key in PERSONALIZATION_COOKIES and \
                rh.request.cookies.get(cookie_key) not in \
                PERSONALIZATION_COOKIES[cookie_key]:
            return False
        elif cookie_key not in GENERIC_COOKIES:
            logging.warning("is_cachable: %s is not a known cookie" %
                            (cookie_key))

    return True

