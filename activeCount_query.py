# -*- coding:utf-8 -*-
# author : zhou xy


import os,sys
from ser_tools.Tools import readFile,chkTools
from conf import settings 
from query.Query import logQuery
from managment.argManagment import argManager
import datetime
from managment.parseArgsManagment import parse_args

check_tools=chkTools()
last_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime('%Y%m%d%H%m%s')[0:14]
FILE_PATH=settings.IPLIST_PATH	
	
	
def query_ics(lQ,am,infos):
	lQ.query_path=os.path.join(infos.get("log_path"),am.log_dt[6:])
	file_name = 'S.LSNSVR_'+am.ser_name+'*trc.*'
	lQ.log_file = file_name
	file_list=lQ.get_file_list()
	log_list = check_tools.filter_log_time(file_list, am.log_dt[4:])
	if not log_list : 
		print("="*8+infos.get("ip")+"="*8)
		print("no such file")
		sys.exit()
	log_list=list(filter(lambda x :int(x.split('.')[-1]) >= int(last_time) ,log_list))
	log_list.append('S.LSNSVR_'+am.ser_name+'.trc')
	print("="*8+infos.get("ip")+"="*8)
	lQ.get_active(log_list,th_count)


def query_ntp(lQ,am,infos):
	lQ.query_path=infos.get("log_path")
	file_name='access-'+am.ser_name.lower()+'-'+am.log_dt+'*log'
	lQ.log_file = file_name
	file_list=lQ.get_file_list()
	log_list = check_tools.filter_log_time(file_list, am.log_dt[4:])
	if not log_list : sys.exit()
	log_list.append('access-'+am.ser_name.lower()+'.log')
	print("="*8+infos.get("ip")+"="*8)
	lQ.get_active(log_list,th_count)
	
	
		
	
if __name__ == '__main__' :
	import threading
	try :
		pcluster = sys.argv[1]
		if pcluster.startswith("-"):
			parse_args(pcluster)
	except IndexError :
		print('\033[1;31;40m%s\033[0m'%"format : sh get_threadCount.sh ��Ⱥ�� ʵ���� �߳�����ֵ���ɲ����룩")
		print ('\033[1;31;40m%s\033[0m'%"���� sh get_threadCount.sh  -h �鿴��ϸ��Ⱥ��Ϣ")
		print ('\033[1;31;40m%s\033[0m'%"���� sh akz.sh -info cluter����IP  ���뼯Ⱥ�鿴��Ⱥ�е�IP��������IP�鿴��IP������Ⱥ")
		#readFile.enum_cluter(FILE_PATH)
		sys.exit()
	try :
		ser_name = sys.argv[2]
	except IndexError :
		print("������ʵ����")
		sys.exit()
	try :
		th_count= sys.argv[3]
	except IndexError :
		th_count = None
	
	cur_date = datetime.datetime.now().strftime('%Y%m%d')
	am = argManager(cluster=pcluster,ser_name=ser_name,log_dt=cur_date)
	for infos in am.query_info[pcluster] :
		lQ = logQuery(am,infos)
		if infos.get("frame")=='ics':
			t=threading.Thread(target=query_ics,args=(lQ,am,infos))
		else :
			t=threading.Thread(target=query_ntp,args=(lQ,am,infos))
		t.start()
		t.join()