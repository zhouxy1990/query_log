# -*- coding:utf-8 -*-
# author : zhou xy
import sys
import paramiko
import time
import os
from ser_tools.Tools import readFile,chkTools
import threading
from conf import settings
from ser_tools.param_ssh import sshConnection
from ser_tools.Managment import Args

date=time.strftime('%Y%m%d',time.localtime(time.time())) 
FILE_PATH=settings.IPLIST_PATH
config=readFile(FILE_PATH)
check_tools=chkTools()
#lock=threading.RLock()

def get_log(ip,path,frame,log_dt,key_word,log_name,ssh):
	command=''
	if frame == 'ics' :
		query_path=os.path.join(path,log_dt[2:])
		stdin,stdout,stderr=ssh.exec_command('cd '+query_path+' ;ls -lrt '+log_name)
		file_list=stdout.readlines()
		if not file_list :
			print('='*5+ip+'='*5+'\n'+' no such file')
			return
		log_list=check_tools.filter_log_time(file_list,log_dt)
		is_gz=check_tools.chk_is_gz(log_list)
		if is_gz:
			command='cd '+query_path+' ;zgrep '+key_word+' '+log_name
			stdin,stdout,stderr=ssh.exec_command(command)
			print ('='*5+ip+'='*5+'\n'+stdout.read())	
		else :
			command='cd '+query_path+' ;fgrep '+key_word+' '+log_name	
			stdin,stdout,stderr=ssh.exec_command(command)
			print ('='*5+ip+'='*5+'\n'+stdout.read())	
		
	elif frame =='ntp' :
		query_path=path
		stdin,stdout,stderr=ssh.exec_command('cd '+query_path+' ;ls -lrt '+log_name)
		file_list=stdout.readlines()
		log_list=map(lambda x:x.split()[8],file_list)
#		log_list=check_tools.filter_log_time(file_list,log_dt)
		if check_tools.chk_is_gz(log_list) :
			command='cd '+query_path+' ;zgrep '+key_word+' '+log_name
		else :
			command='cd '+query_path+' ;fgrep '+key_word+' '+log_name
		stdin,stdout,stderr=ssh.exec_command(command)
		print ('='*5+ip+'='*5+'\n'+stdout.read().decode('utf8'))


def fetch_log(cluter,ip,user_name,path,frame,log_dt,key_word,log_name):
	file_list=[]
	log_list=[]
	ssh_conn=sshConnection(ip,user_name)
	ssh=ssh_conn.get_conn()
	try :
		get_log(ip,path,frame,log_dt,key_word,log_name,ssh)
#	except AttributeError :
#		print ('{} query error .... please try again '.format(ip))
#		fetch_log(cluter,ip,user_name,path,frame,log_dt,key_word,log_name)
	except ValueError as e:
		if 'time data' in str(e) :
			print ('输入的时间{}格式错误'.format(log_dt).decode('utf8'))
		else :
			print (e)
	except KeyboardInterrupt :
		print ('you have stopped the threading...')
	except Exception as e :
		print (e)
	finally :
		ssh_conn.close_conn()

def main():
	args = Args()
	try :
		pcluter=sys.argv[1]
		if pcluter == '-info' :
			arg = args.add_arg(pcluter,help_inf="输入集群查看集群中的IP或者输入IP查看该IP归属集群")
			if hasattr(arg,pcluter.replace('-','')):	
				info = getattr(arg,pcluter.replace('-',''))
				detail_info = config.show_detail_info(settings.IPLIST_PATH,info)
			return
		if pcluter == '-h' or pcluter == '-H' or pcluter == 'help' :
			config.show_cluter_info(FILE_PATH)
			return
		log_dt=sys.argv[2]
		key_word=sys.argv[3]
		log_name=sys.argv[4]	
	except IndexError :
		print ('\033[1;31;40m%s\033[0m'%"输入 sh akz.sh help 或者 -h 查看详细集群信息".decode('utf8'))
		print ('\033[1;31;40m%s\033[0m'%"输入 sh akz.sh -info cluter或者IP  输入集群查看集群中的IP或者输入IP查看该IP归属集群".decode('utf8'))
		config.enum_cluter(FILE_PATH)
	else :
		ip_info=config.read_by_cluter(pcluter)
		if pcluter and  key_word and log_name:
			for each in ip_info :
				cluter=each.split(',')[0]
				ip=each.split(',')[1]
				user_name=each.split(',')[2]
				path=each.split(',')[3]
				frame=each.split(',')[4].replace('\n','')
				t=threading.Thread(target=fetch_log,args=(cluter,ip,user_name,\
					path,frame,log_dt,key_word,log_name))
				t.start()
		else :
			print (' sh akz.sh cluter  time  key_word  log_name')

		
if __name__=='__main__':

	main()