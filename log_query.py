# -*- coding:utf-8 -*-
# author : zhou xy


import threading
import os,sys
from ser_tools.Tools import readFile,chkTools
from conf import settings 
from query.Query import logQuery
from managment.argManagment import argManager
from managment.parseArgsManagment import parse_args
FILE_PATH=settings.IPLIST_PATH
check_tools=chkTools()
import time
rlock=threading.RLock()

def main(am,infos):
	lQ = logQuery(am,infos)
	if infos.get("frame") == "ics" :
		lQ.query_path = os.path.join(infos['log_path'],am.log_dt[2:])
	else :
		lQ.query_path = infos.get("log_path")
	file_list=lQ.get_file_list()
	log_list=check_tools.filter_log_time(file_list,am.log_dt)
	if not log_list :
		rlock.acquire()
		#time.sleep(0.05)
		print("="*8+'ip:'+infos.get("ip")+',cluster:'+infos.get("cluster")+"="*8+"\n"+"no such file")
		rlock.release()
		return
	is_gz=check_tools.chk_is_gz(log_list)
	result=lQ.get_log(is_gz)
	if infos.get("frame") == "lemon" :
		print("="*8+'ip:'+infos.get("ip")+',cluster:'+infos.get("cluster")+"="*8+"\n"+result.decode("utf8"))
	else :
		print("="*8+'ip:'+infos.get("ip")+',cluster:'+infos.get("cluster")+"="*8+"\n"+result)
	
def _args():
	try :
		pcluter=sys.argv[1]
		if pcluter.startswith("-"):
			parse_args(pcluter)
		log_dt=sys.argv[2]
		key_word=sys.argv[3]
		log_name=sys.argv[4]	
	except IndexError :
		print ('\033[1;31;40m%s\033[0m'%"输入 sh akz.sh  -h 查看详细集群信息")
		print ('\033[1;31;40m%s\033[0m'%"输入 sh akz.sh -info cluter或者IP  输入集群查看集群中的IP或者输入IP查看该IP归属集群")
		#readFile.enum_cluter(FILE_PATH)
		sys.exit()
	else :
		am = argManager(cluster=pcluter,log_dt=log_dt,key_word=key_word,log_file=log_name)
		if am :
			for infos in am.query_info[pcluter] :
				t=threading.Thread(target=main,args=(am,infos))
				t.start()

if __name__ == '__main__' :
	_args()