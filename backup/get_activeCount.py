# -*- coding:utf-8 -*-
import sys
from ser_tools.Tools import readFile,chkTools
import datetime
import os
from ser_tools.log_service import SSH_Operation
import paramiko
import re
from conf import settings
import threading
rlock=threading.RLock()
from ser_tools.param_ssh import sshConnection


FILE_PATH=settings.IPLIST_PATH
config=readFile(FILE_PATH)
check_tools = chkTools()
cur_date = datetime.datetime.now().strftime('%Y%m%d')
last_time = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime('%Y%m%d%H%m%s')[0:14]
__QUERY_NUM=settings.ACTIVE_QUERY_NUM #最终查询条数
__MIN_COUNT_ICS=settings.ICS_MIN_THREAD_COUNT #取出的最小线程数
__MIN_COUNT_NTP=settings.NTP_MIN_THREAD_COUNT
__PATTERN_ICS=r'activeCount:\[(.*?)\]'
__PATTERN_NTP=r'\]\: \[(.*?)\] \- \{'
def get_count(ssh,log_path,log_file,frame):
	#获取线程数
	if frame=='ics':
		command='cd '+log_path+';fgrep activeCount '+log_file
		stdin,stdout,stderr=ssh.exec_command(command)
		result_list=stdout.readlines()
		if not result_list :return
		result_list=filter(lambda x : int (re.findall(__PATTERN_ICS,x)[0])>= __MIN_COUNT_ICS,result_list)
	elif frame =='ntp' :
		command='cd '+log_path+"; egrep '\]\: \[(.*?)\] \- \{' "+log_file
		stdin,stdout,stderr=ssh.exec_command(command)
		result_list=stdout.readlines()
		if not result_list :return
		result_list=filter(lambda x : int (re.findall(__PATTERN_NTP,x)[0])>= __MIN_COUNT_NTP,result_list)
	return result_list

def query_ics(ssh,ssho,log_path,file_name,s_name):
	if log_path and file_name :
			file_list=ssho.get_log_file(log_path,file_name)
			log_list = check_tools.filter_log_time(file_list, cur_date[4:])
			if not log_list : return
			log_list=filter(lambda x :int(x.split('.')[-1]) >= int (last_time) ,log_list)
			log_list.append('S.LSNSVR_'+s_name+'.trc')
			result_list=[]
			if log_list :
				for log_file in log_list :
					tmp_list=get_count(ssh,log_path,log_file,'ics')
					result_list.extend(tmp_list)
			else :
				return
	else :
		return
	return result_list

def query_ntp(ssh,ssho,log_path,file_name,s_name):
	def cmp_time(file_info):
		last_hour=(datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime('%Y%m%d%H%m%s')[8:10]	
		log_hour=file_info.split()[7].split(':')[0]
		if int(log_hour) >= int(last_hour):
			return file_info
	if log_path and file_name :
		file_list=ssho.get_log_file(log_path,file_name)
		file_list=filter(cmp_time,file_list)
#		print (file_list)
		log_list = check_tools.filter_log_time(file_list, cur_date[4:])
		if not log_list : return
		result_list=[]
		for log_file in log_list :
			tmp_list=get_count(ssh,log_path,log_file,'ntp')
			result_list.extend(tmp_list)
	else : return
	return result_list
	
def get_log(ip,user_name,path,frame,s_name):
	result_list=[]
	ssh_conn=sshConnection(ip,user_name)
	ssh=ssh_conn.get_conn()
	if not ssh : return
	try :
		ssho=SSH_Operation(ssh)
	except Exception as e :
		print ('='*8+ip+'='*8)
		print(e)
	else :
		if frame == 'ics' :
			log_path=os.path.join(path,cur_date[6:])
			file_name='S.LSNSVR_'+s_name+'*trc.'
			result_list=query_ics(ssh,ssho,log_path,file_name,s_name)
			if not result_list :return
			result_list=sorted(result_list,key=lambda x : re.findall(__PATTERN_ICS,x)[0],reverse=True)
		elif frame == 'ntp' :
			log_path=path
			file_name='access-'+s_name.lower()+'-'+cur_date+'*log'
			result_list=query_ntp(ssh,ssho,log_path,file_name,s_name)
			if not result_list :return
			result_list=sorted(result_list,key=lambda x : re.findall(__PATTERN_NTP,x)[0],reverse=True)
		if result_list :	
			sort_list=[]
			for num,item in enumerate(result_list) :
				if num < __QUERY_NUM :
					sort_list.append(item)
				else :
					break
			#rlock.acquire()
			print ('='*8+ip+'='*8)
			print (''.join(sort_list))
			#rlock.release()
	finally :
		ssh_conn.close_conn()


def main():
	try :
		pcluter=sys.argv[1]
		if pcluter == '-h' or pcluter == '-H' or pcluter == 'help' :
			config.show_cluter_info(FILE_PATH)
			return
		s_name=sys.argv[2]
	except IndexError :
		print('\033[1;31;40m%s\033[0m'%"format : sh get_threadCount.sh 集群名 实例名")
		print ('\033[1;31;40m%s\033[0m'%"输入 sh get_threadCount.sh help 或者 -h 查看详细集群信息")
		config.enum_cluter(FILE_PATH)
	else :
		ip_info=config.read_by_cluter(pcluter)
		if pcluter:
			for each in ip_info :
				cluter=each.split(',')[0]
				ip=each.split(',')[1]
				user_name=each.split(',')[2]
				path=each.split(',')[3]
				frame=each.split(',')[4].replace('\n','')
				t=threading.Thread(target=get_log,args=(ip,user_name,path,frame,s_name))
				#get_log(ip,user_name,path,frame,s_name)
				t.start()
				t.join()
if __name__=='__main__':
	main()