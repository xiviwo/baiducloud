
import inspect
import sys
import math
import random 
import codec
import time
import re
from log import logger
import threading
import traceback
from gi.repository import GLib

def info(str):
	if settings.DEBUG:
		print(u"\033[42mINFO:%s\033[0m"%str)
	else:
		
		print(u"INFO:%s"%str)

def to_unicode(s):
	
	if isinstance(s, str):
		s = unicode(s,'utf-8')

		return s
	elif isinstance(s, unicode):

		return s
	
	else:
		return unicode(str(s),'utf-8')
		
def to_string(s):
	if isinstance(s, str):
		return s
	elif isinstance(s, unicode):
		return s.encode("utf-8")
	else:
		return str(s)



def myname():
	return inspect.stack()[1][3].title()

def cbs_token():
	num = int(math.floor(random.random()*2147483648))
	
	return "bd__cbs__" + codec.base36encode(num).lower()
def tt():
	return str(int(time.time()*1000))
def fix_json(j):
	j = re.sub('.*\(([^\)]*)\)',"\g<1>",j)

	j = re.sub(r"(,?)(\w+?)\s+?:", r"\1'\2' :", j)

	j = j.replace("'", "\"")
	return j

def tosign(sign3,sign1):
	a = []
	p = []
	o = b''
	v = len(sign3)
	for q in range(256):
		a.append(ord(sign3[(q%v):(q%v+1)]))
		p.append(q)
	
	u=0
	for q in range(256):
		u = ( u + p[q] + a[q] ) % 256
		t = p[q]
		p[q] = p[u]
		p[u] = t
	
	i = 0
	u = 0
	for q in range(len(sign1)):
		i = (i + 1 ) % 256
		u = (u + p[i]) %256
		t = p[i]
		p[i] = p[u]
		p[u] = t;
		k = p[((p[i] + p[u]) % 256)]
		
		o += bytes([(ord(sign1[q])^k)])
	
	return o

def async_call(func, *args, callback=None):
    '''Call `func` in background thread, and then call `callback` in Gtk main thread.

    If error occurs in `func`, error will keep the traceback and passed to
    `callback` as second parameter. Always check `error` is not None.
    '''
    def do_call():
        result = None
        error = None

        try:
            result = func(*args)
        except Exception:
            error = traceback.format_exc()
            logger.error(error)
        if callback:
            GLib.idle_add(callback, result, error)

    thread = threading.Thread(target=do_call)
    thread.daemon = True
    thread.start()

