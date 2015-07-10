from random import randint
import os
PAN_HOST = "pan.baidu.com"
PAN_INDEX = "http://" + PAN_HOST
DISK_HOME = PAN_INDEX + '/disk/home'
FILE_MANAGER	= PAN_INDEX + "/api/filemanager"
CLOUD_DL = PAN_INDEX + "/rest/2.0/services/cloud_dl"
PASSPORT_HOST = 'passport.baidu.com'
PASSPORT_INDEX = "https://" + PASSPORT_HOST
PASSPORT_API = PASSPORT_INDEX + "/v2/api"
USERAGENTLIST = [ 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',]

USERAGENT =  USERAGENTLIST[randint(0,len(USERAGENTLIST)-1)]

GREEN = u"\033[42m%s\033[m"
BLUE = u"\033[44m%s\033[m"
RED = u"\033[41m%s\033[0m"
WHITE= u"%s"

SAVINGPATH = os.path.expanduser("~/Downloads")
