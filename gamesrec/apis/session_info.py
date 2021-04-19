import re
import warnings
from django.contrib.gis.geoip2 import HAS_GEOIP2
from django.utils.translation import ugettext_lazy as _

BROWSERS = (
    (re.compile('Edge'), _('Edge')),
    (re.compile('Chrome'), _('Chrome')),
    (re.compile('Safari'), _('Safari')),
    (re.compile('Firefox'), _('Firefox')),
    (re.compile('Opera'), _('Opera')),
    (re.compile('IE'), _('Internet Explorer')),
)
DEVICES = (
    (re.compile('Windows Mobile'), _('Windows Mobile')),
    (re.compile('Android'), _('Android')),
    (re.compile('Linux'), _('Linux')),
    (re.compile('iPhone'), _('iPhone')),
    (re.compile('iPad'), _('iPad')),
    (re.compile('Mac OS X 10[._]9'), _('OS X Mavericks')),
    (re.compile('Mac OS X 10[._]10'), _('OS X Yosemite')),
    (re.compile('Mac OS X 10[._]11'), _('OS X El Capitan')),
    (re.compile('Mac OS X 10[._]12'), _('macOS Sierra')),
    (re.compile('Mac OS X 10[._]13'), _('macOS High Sierra')),
    (re.compile('Mac OS X'), _('OS X')),
    (re.compile('NT 5.1'), _('Windows XP')),
    (re.compile('NT 6.0'), _('Windows Vista')),
    (re.compile('NT 6.1'), _('Windows 7')),
    (re.compile('NT 6.2'), _('Windows 8')),
    (re.compile('NT 6.3'), _('Windows 8.1')),
    (re.compile('NT 10.0'), _('Windows 10')),
    (re.compile('Windows'), _('Windows')),
)

def get_user_info_log(request):
    return {
        'user':request.user,
        'ip_address':get_ip(request),
        'user_agent':get_user_agent(request)
    }

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')

_geoip = None

def geoip():
    global _geoip
    if _geoip is None:
        if HAS_GEOIP2:
            from django.contrib.gis.geoip2 import GeoIP2
            try:
                _geoip = GeoIP2()
            except Exception as e:
                warnings.warn(str(e))
    return _geoip

def device(value, *args, **kwargs):
    browser = None
    for regex, name in BROWSERS:
        if regex.search(value):
            browser = name
            break
    device = None
    for regex, name in DEVICES:
        if regex.search(value):
            device = name
            break
    if browser and device:
        if 'json' in kwargs and kwargs['json'] == True:
            return {'browser':browser,'device':device}
        return f'{browser} {device}'
    if browser:
        if 'json' in kwargs and kwargs['json'] == True:
            return {'browser':browser,'device':None}
        return browser
    if device:
        if 'json' in kwargs and kwargs['json'] == True:
            return {'browser':None,'device':device}
        return device
    return None


def location(value):
    try:
        location = geoip() and geoip().city(value)
    except Exception:
        try:
            location = geoip() and geoip().country(value)
        except Exception as e:
            warnings.warn(str(e))
            location = None
    if location and location['country_name']:
        return f"{location['city']}, {location['country_name']}" if 'city' in location and location['city'] else location['country_name']
    return None
