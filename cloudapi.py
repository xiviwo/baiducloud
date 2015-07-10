from log import logger
import utils
import urllib.request, urllib.parse, urllib.error
import auth
import os
import json
import re
from weblib import fetch
import base64
import settings
from const import * 
from gi.repository import GdkPixbuf
from gi.repository import Gtk
from urllib.parse import urlparse
from VcodeDialog import VcodeDialog
def list_path(path,num,dry,bdstoken):
	logger.info("Listing path %s."%path)
	settings.DRY = dry
	header = {
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	t = utils.tt()
	t2 = str(int(t) + 2)
	if path:
		_path = urllib.parse.urlencode({"dir":path})
	else:
		_path = urllib.parse.urlencode({"dir":'/'})
	url = PAN_INDEX + '/api/list?channel=chunlei&clienttype=0&web=1&num=' + \
	str(num) + '&t=' + t + '&page=1&' + _path + \
	'&showempty=0&order=time&desc=1&_='+ t2 +  \
	 '&bdstoken=' + bdstoken + "&app_id=250528"
	xml = fetch(url,{},utils.myname(),header,path)

	list_json = json.loads(xml.decode("utf-8"))
	if list_json:
		return list_json
	else:	
		return None


def get_list(list_json):

	filelist = []
	if list_json and 'list' in list(list_json.keys()):
		for i,item in enumerate(list_json['list']):
			num = i
			filename = item['server_filename']
			path = os.path.dirname(item['path'])
			size = item['size']
			isdir= item['isdir']
			fsid = str(item['fs_id'])
			cate = item['category']
			if 'thumbs' in list(item.keys()):
				#logger.debug("Get thumb for file: %s"%filename)
				#logger.debug("THUMBS: %s"%str(item['thumbs']))
				if 'url1' in list(item['thumbs'].keys()):
					thumb = item['thumbs']['url1']
				elif 'icon' in list(item['thumbs'].keys()):
					thumb = item['thumbs']['icon']
				else:
					thumb = item['thumbs']['url2']
					
				
			else:
				thumb = None
				

			dw=["B","K","M","G"]
			for i in range(4):
				_dw=dw[i]
				if size>=1024:
					size=size/1024
				else:
					break
			size="%.1f%s"%(size,_dw)
			filelist.append((num,thumb,filename,size,path,isdir,fsid,cate))
	
		return filelist
	else:
		return None


def clean_up(tokens,clist):
	report = []
	for index,filename,size,path,isdir,fsid in clist:
		link,fsid = get_dlink(tokens,fsid,path,index)
		if not isdir and not link:
			logger.info("Removing file %s ."%path)
			remove_invalid_file(path)
			report.append((filename,path))
			
		elif isdir:
			list_json = list_path(path,300,False)
			report +=clean_up(get_list(list_json))
	
	return report
		
def remove_invalid_file(path):
	
	info ("File invalid,deleting %s."%path)
	filelist = '["%s"]'%path
	logger.debug("filelist: %s "%str(filelist))
	delete_file(filelist)
	parentdir= os.path.dirname(path)
	sizeofdir = list_path(parentdir,300,False)
	logger.debug("sizeofdir %s:"%parentdir,sizeofdir)
	if sizeofdir == 0 :
		logger.info("Resulting size of dir is 0,deleting dir %s"%parentdir)
		filelist = '["%s"]'%parentdir
		delete_file(filelist)
counter = 0
def get_dlink(tokens,fid,path,num):
	global counter
	settings.DRY = False
	logger.debug("file path: %s "%path)
	bdstoken,sign1,sign3,timestamp = tokens
	
	header = {
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	data = {
		'sign':base64.b64encode(utils.tosign(sign3,sign1)).decode('utf-8'),
		'timestamp':timestamp,
		'fidlist':'[%s]'%fid,
		'type':'dlink',
		'bdstoken':bdstoken,
		'channel':'chunlei',
		'clienttype':0,
		'web':1,
		'app_id':'250528',
		}
	url = 'http://pan.baidu.com/api/download?' + urllib.parse.urlencode(data)
	
	xml = fetch(url,{},fid+"_json",header,os.path.dirname(path))
	list_json = json.loads(xml.decode("utf-8"))
	
	if list_json['errno'] == 112 or list_json['errno'] == 113 :
		
		if counter < 2:
			counter +=1
			tokens = auth.index()
			return get_dlink(tokens,fid,path,num)
		else:
			return (None,fid,num)
		
	elif list_json['errno'] == -1:
		#remove_invalid_file(path)
		
		return (None,fid,num)
	elif list_json['errno'] == 0:
		
		settings.DRY = True
	
		return (list_json['dlink'][0]['dlink'],fid,num)
	else:
		logger.info ("Unknow Error, return none.")
		return (None,fid,num)
	

def _download(cols):
	
	for link,fn in cols:
		if link:
			url = re.sub("http://([^/]*)/",'http://hot.baidupcs.com/',link)
			#http://hot.baidupcs.com/
		
			cmd=['aria2c','-c', '-s1', '-x1','-j1', url,'-o',fn]
			cmd="aria2c -c -s1 -x1 -j1 -o '%s' '%s'"%(fn,url)
			logger.info( cmd )
			os.system("cd %s && %s"%(downpath,cmd))
		else:
			logger.info("Link of file %s is invalid,pass"%fn)
			pass

def delete_task(bdstoken,taskid):
	url = CLOUD_DL + "?bdstoken=" +  bdstoken + "&task_id=" + \
	taskid + "&method=delete_task&app_id=250528&t=" + utils.tt() + \
	"&bdstoken=" +  bdstoken + "&channel=chunlei&clienttype=0&web=1&app_id=250528"
	xml = fetch(url,{},utils.myname(),{})
	j = json.loads(xml.decode("utf-8"))
	logger.debug("json: %s "% str(j))
	return (j,taskid)

def cancel_task(bdstoken,taskid,taskname):
	url = CLOUD_DL + "?bdstoken=" +  bdstoken + "&task_id=" + \
	taskid + "&method=cancel_task&app_id=250528&t=" + utils.tt() + \
	"&bdstoken=" +  bdstoken + "&channel=chunlei&clienttype=0&web=1&app_id=250528"

	xml = fetch(url,{},utils.myname(),{})
	j = json.loads(xml.decode("utf-8"))
	logger.debug("json: %s "% str(j))
	return (j,taskid,taskname)

def query_task(bdstoken,taskid):
	url =  CLOUD_DL + "?bdstoken=" +  bdstoken + "&task_ids=" + \
	taskid + "&op_type=1&method=query_task&app_id=250528&t=" + utils.tt() + \
	"&bdstoken=" +  bdstoken + "&channel=chunlei&clienttype=0&web=1&app_id=250528"
	xml = fetch(url,{},utils.myname(),{})
	j = json.loads(xml.decode("utf-8"))
	logger.debug("json: %s "% str(j))
	return (j,taskid)
def list_task(bdstoken):
	url = CLOUD_DL + '?bdstoken=' +  bdstoken + \
	'&need_task_info=1&status=255&start=0&limit=100&method=list_task&app_id=250528&t=' + \
	 utils.tt() + '&bdstoken=' +  bdstoken + '&channel=chunlei&clienttype=0&web=1&app_id=250528'
	xml = fetch(url,{},utils.myname(),{})
	j = json.loads(xml.decode("utf-8"))
	
	return j

def add_task(bdstoken,t_url,save_path,dia):
	header = {
	'Content-Type':'application/x-www-form-urlencoded',
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	url = CLOUD_DL + '?bdstoken=' + bdstoken + '&channel=chunlei&clienttype=0&web=1'
	post = {
	'method':'add_task',
	'app_id':'250528',
	'source_url':t_url,
	'save_path':save_path,
	'type':'3',
	}
	xml = fetch(url,post,utils.myname(),header,save_path)
	j = json.loads(xml.decode("utf-8"))
	logger.debug("json: %s "% str(j))
	
	if 'error_code' in list(j.keys()):
		logger.info(j['error_msg'])
		if j['error_code'] != 36022 :
			while 'vcode' in list(j.keys()):
				vcode = j['vcode']
				logger.info(vcode)
				imgurl = j['img']
				#f=open(vimg,"wb")
				#fp = fetch(imgurl,{},"Input Vcode")
				#f.write(fp)
				#f.close()
				#try:
				#	subprocess.Popen(['xdg-open', vimg])
				#except:
				#	print("please open file %s to check the vcode."%vimg)
				#mag = re.search('(&.*$)',t_url).group(1)
				#task_name = dict(urllib.parse.parse_qsl(mag))['dn']

				#logger.info("Please input vcode for task: %s ."%(task_name))
				vd = VcodeDialog(dia,imgurl)
				vd.new_url(imgurl)
				response = vd.run()
				print(response)
				if response == 22:
					print("The OK button was clicked")
					vf = vd.get_user_input()
					vd.destroy()
				elif  response == Gtk.ResponseType.DELETE_EVENT:
					vd.destroy()
				#input("verification code # ").strip()
				
				add = {
				'file_sha1':'',
				'selected_idx':'1,2,3,4',
				'task_from':'0',
				't':utils.tt(),
				'type':4,
				'input':vf,
				'vcode':vcode,
				}
				print(add)
				post.update(add)
				xml = fetch(url,post,"TryWithVcode",header,save_path)
				j = json.loads(xml.decode("utf-8"))
				logger.debug("json: %s "% str(j))
				if 'error_code' in list(j.keys()):
					logger.info(j['error_msg'])
			return j
		else:
			
			return j['error_msg']
	logger.debug("json: %s "% str(j))

	return j
def batch_add(fn):
	for f in open(fn).read().split('\n'):
		if f:
			add_task(bdstoken,f,'/')

def delete_file(bdstoken,filelist):
	header = {
	'Content-Type':'application/x-www-form-urlencoded',
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	url = FILE_MANAGER + \
	'?channel=chunlei&clienttype=0&web=1&opera=delete&bdstoken=' + \
	bdstoken + "&app_id=250528"
	post = {
	'filelist':filelist,
	}
	path = os.path.dirname(filelist.strip('["').strip('"]').split(',')[0])
	xml = fetch(url,post,utils.myname(),header,path)
	return xml

def move_file(bdstoken,filelist):
	header = {
	'Content-Type':'application/x-www-form-urlencoded',
	'Host':PAN_HOST,
	'Referer':DISK_HOME,
	}
	url = FILE_MANAGER + \
	'?channel=chunlei&clienttype=0&web=1&opera=move&bdstoken=' + \
	bdstoken + "&app_id=250528"
	post = {
	'filelist':filelist,
	}
	xml = fetch(url,post,utils.myname(),header)
	return xml

def search_mag(s,dry=True):
	settings.DRY = dry
	header = {
	"host":"www.thepiratebay.se",
	"method":"GET",
	}
	url = "https://www.thepiratebay.se/s/?q=" + s + \
	"&porn=on&category=0&page=0&orderby=99"
	xml = fetch(url,{},utils.myname(),header)
	
	return xml
