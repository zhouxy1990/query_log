# -*- coding:utf-8 --


'''
from ser_tools.param_ssh import sshConnection
ssh_con = sshConnection('172.29.74.12','admlog',22)
try :
	ssh = ssh_con.get_conn()
	print(ssh)
except Exception as e :
	print(e)
finally :
	ssh_con.close_conn()


'''
import os,sys
from ser_tools.Tools import readFile,chkTools
from conf import settings 
from query.Query import logQuery
#config = readFile(settings.IPLIST_PATH)
from managment.argManagment import argManager
import datetime
check_tools=chkTools()
last_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime('%Y%m%d%H%m%s')[0:14]
	
def query_ics(lQ,am,infos):
	lQ.query_path=os.path.join(infos.get("log_path"),am.log_dt[6:])
	file_name = 'S.LSNSVR_'+am.ser_name+'*trc.*'
	lQ.log_file = file_name
	file_list=lQ.get_file_list()
	log_list = check_tools.filter_log_time(file_list, am.log_dt[4:])
	if not log_list : sys.exit()
	log_list=filter(lambda x :int(x.split('.')[-1]) >= int (last_time) ,log_list)
	log_list.append('S.LSNSVR_'+am.ser_name+'.trc')
	print("="*8+infos.get("ip")+"="*8)
	lQ.get_active(log_list)


def query_ntp(lQ,am,infos):
	lQ.query_path=infos.get("log_path")
	file_name='access-'+am.ser_name.lower()+'-'+am.log_dt+'*log'
	lQ.log_file = file_name
	file_list=lQ.get_file_list()
	log_list = check_tools.filter_log_time(file_list, am.log_dt[4:])
	print(log_list)
	if not log_list : sys.exit()
	lQ.get_active(log_list)
	
	
		
	
if __name__ == '__main__' :
	import threading
	pcluster = '172.29.112.31'
	ser_name = 'usermanager'
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
	

