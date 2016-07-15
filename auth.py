
from const import *
import utils
from weblib import fetch,WebPage
from log import logger
import subprocess
from codec import RSA_encrypt
import re
import json
import random


def index():
	url = PAN_INDEX
	header = { 		
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	sign1 = ''
	sign3 = ''
	bdstoken = ''
	timestamp = ''
	xml = fetch(url,{},utils.myname(),header).decode('utf-8')
	signmatch = re.search("yunData\.sign1\s*=\s*'([^']*)'",xml)
	if signmatch:
		sign1 = signmatch.group(1)
	logger.debug('sign1: %s '%sign1 )


	bdstokenmatch = re.search('MYBDSTOKEN\s*=\s*"([^"]*)"',xml)
	if bdstokenmatch:
		bdstoken = bdstokenmatch.group(1)
	logger.debug('bdstoken: %s '%bdstoken)


	sign3match = re.search("yunData\.sign3\s*=\s*'([^']*)'",xml)
	if sign3match:
		sign3 = sign3match.group(1)
	logger.debug('sign3: %s '%sign3 )

	timestampmatch = re.search("yunData\.timestamp\s*=\s*'([^']*)'",xml)
	if timestampmatch:
		timestamp = timestampmatch.group(1)
	logger.debug('timestamp: %s '%timestamp )

	return (bdstoken,sign1,sign3,timestamp)

def get_bdtoken():
	url = PAN_INDEX
	header = { 		
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	xml = fetch(url,{},utils.myname())
	bdstoken = xml.search('MYBDSTOKEN\s*=\s*"([^"]*)"')
	logger.debug('bdstoken: %s '%bdstoken)

	if bdstoken:
		return bdstoken
	else:
		return None


def get_sign1():
	url = PAN_INDEX
	header = { 		
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	xml = fetch(url,{},utils.myname())
	sign1 = xml.search("yunData.sign1\s*=\s*'([^']*)';") 
	logger.debug('sign1: %s '%sign1 )
	if sign1:
		return sign1
	else:
		return None


def get_sign3():
	url = PAN_INDEX
	header = { 		
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	xml = fetch(url,{},utils.myname())	
	sign3 = xml.search("yunData.sign3\s*=\s*'([^']*)';") 
	logger.debug('sign3: %s '%sign3 )
	if sign3:
		return sign3
	else:
		return None

def get_timestamp():
	
	url = PAN_INDEX
	header = { 		
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	xml = fetch(url,{},utils.myname())	
	timestamp = xml.search("yunData.timestamp\s*=\s*'([^']*)';") 
	logger.debug('timestamp: %s '%timestamp )

	if timestamp:
		return timestamp
	else:
		return None

def get_token():
	header = { 'Host': PASSPORT_HOST,
	'Referer': PAN_INDEX,
	}
	cbs = utils.cbs_token()
	login_init = utils.tt()
	url = PASSPORT_API + '/?getapi&tpl=netdisk&apiver=v3&tt='+ \
	login_init + '&class=login&logintype=basicLogin&callback=' + cbs
	logger.debug('url:: %s '%url)
	xml = fetch(url,{},utils.myname(),header)
	xml = utils.fix_json(xml.decode('utf-8'))
	token =  json.loads(xml)['data']['token']
	logger.debug("token:%s"%token)
	
	return token


def get_public_key(token):

	header = { 'Host':	PASSPORT_HOST,
	'Referer':	PAN_INDEX,
	}
	cbs = utils.cbs_token()

	url = 'https://passport.baidu.com/v2/getpublickey?token=' + \
	token + '&tpl=netdisk&apiver=v3&tt=' + utils.tt() + '&callback=' + cbs
	xml = fetch(url,{},utils.myname(),header).decode('utf-8')
	keystr = re.search("\(([^\)]*)\)",xml).group(1).replace("'", '"').replace('\t', '')
	logger.debug("key str:%s"%keystr)
	keydict = eval(keystr)
	logger.debug("keydict:%s"%keydict)
	rsakey = keydict['key']
	pubkey = keydict['pubkey']
	logger.debug("rsakey:%s"%rsakey)
	logger.debug("pubkey:%s"%pubkey)
	return (rsakey,pubkey)

def login_history(token):

	header = { 'Host':	PASSPORT_HOST,
	'Referer':	PAN_INDEX,
	}
	cbs = utils.cbs_token()
	url = PASSPORT_API + '/?loginhistory&token=' + token + \
	'&tpl=netdisk&apiver=v3&tt=' + utils.tt() + '&callback=' + cbs
	xml = fetch(url,{},utils.myname(),header)
	xml = utils.fix_json(xml)
	return xml

def login_check(username,token):
	header = { 'Host':	PASSPORT_HOST,
	'Referer':	PAN_INDEX,
	}
	cbs = utils.cbs_token()
	url = PASSPORT_API + '/?loginhistory&token=' + token + \
	'&tpl=netdisk&apiver=v3&tt=' + utils.tt() + '&username=' + \
	username + '&isphone=false&callback=' + cbs
	xml = fetch(url,{},utils.myname(),header)
	xml = utils.fix_json(xml)
	return xml

def login_vcode():

	url = 'https://passport.baidu.com/cgi-bin/genimage?' + codeString
	f=open(vimg,"wb")
	fp = fetch(url,{},utils.myname())
	f.write(fp)
	f.close()
	try:
		subprocess.Popen(['xdg-open', vimg])
	except:
		print("Please open %s to check verification code"%vimg)
	print("Please input verification code for %s, vcode : %s："%(url,vcode))
	vf=input("Verification Code # ").strip()
	return vf 

def login(rsakey,pubkey,username,password,token):
	url = PASSPORT_API + '/?login'
	login_start = utils.tt()
	header = { 
	'Host'	:PASSPORT_HOST,
	'Referer'	:PAN_INDEX,
	'Origin':PAN_INDEX,
	'Content-Type'	:'application/x-www-form-urlencoded',
	}
	logger.debug("encrypted pw: %s "%RSA_encrypt(pubkey, password))
	post = {
	'apiver':'v3',
	'callback':'parent.'+utils.cbs_token(),
	'charset':'utf-8',
	'codestring':'',
	'isPhone':'false',
	'loginmerge':'true',
	'logintype':'basicLogin',
	'mem_pass':'on',
	'password':RSA_encrypt(pubkey, password),#password,
	'ppui_logintime':str(random.randint(52000, 58535)),#int(login_start)-int(login_init),
	'quick_user':'0',
	'safeflg':'0',
	'staticpage':'http://pan.baidu.com/res/static/thirdparty/pass_v3_jump.html',
	'token':token,
	'tpl':'netdisk',
	'tt':login_start,
	'u':PAN_INDEX,
	'username':username,
	'verifycode':''	,
	'subpro':'',
	'logLoginType':'pc_loginBasic',
	'crypttype':'12',
	'rsakey':rsakey,
	'idc:':'',
	}
	xml = fetch(url,post,utils.myname(),header).decode('utf-8')
	img = re.search('"(err_no=[^"]*)"',xml).group(1)
	import urllib.parse
	idict = dict(urllib.parse.parse_qsl(img))
	logger.debug("idict : %s"%idict)

	return (xml,idict)

def relogin(rsakey,pubkey,username,password,token,vf,codeString):
	url = PASSPORT_API + '/?login'
	login_start = utils.tt()
	header = { 
	'Host'	:PASSPORT_HOST,
	'Referer'	:PAN_INDEX,
	'Origin':PAN_INDEX,
	'Content-Type'	:'application/x-www-form-urlencoded',
	}
	post = {
	'staticpage':'http://pan.baidu.com/res/static/thirdparty/pass_v3_jump.html',
	'charset':'utf-8',
	'token':token,
	'tpl':'netdisk',
	'subpro':'',
	'apiver':'v3',
	'tt':login_start,
	'codestring':codeString,
	'safeflg':'1',
	'u':PASSPORT_INDEX + "/",
	'isPhone':'false',
	'quick_user':'0',
	'logintype':'basicLogin',
	'logLoginType':'pc_loginBasic',
	'loginmerge':'true',
	'username':'abcdefg',
	'password':RSA_encrypt(pubkey, 'afds'),
	'verifycode':vf,
	'mem_pass':'on',
	'rsakey':rsakey,
	'crypttype':'12',
	'ppui_logintime':str(random.randint(52000, 58535)),
	'callback':'parent.'+cbs_token(),
	'idc:':'',
	}
	xml = self.fetch(url,post,myname(),header).decode('utf-8')
	img = re.search('"(err_no=[^"]*)"',xml).group(1)
	import urllib.parse
	idict = dict(urllib.parse.parse_qsl(img))
	logger.debug("idict : %s"%idict)
	return (xml,idict)
