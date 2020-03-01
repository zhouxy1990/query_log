# -*- coding:gbk -*-
import sys
from ser_tools.Tools import readFile,chkTools
import datetime
import os
import paramiko
import re
from conf import settings


__PATTERN_ICS=r'\[(.[0-9]*?)\]$'
__MIN_DUR=settings.MIN_DURATION
file_path=settings.IPLIST_PATH
config=readFile(file_path)
check_tools = chkTools()
cur_date = datetime.datetime.now().strftime('%Y%m%d')

def get_connect(ip, user_name):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, 22, user_name, timeout=2.5)
	return ssh

def ics_database(ssh,log_path,file_name):
	command="cd "+log_path+" ; fgrep ' INFO - ' "+file_name
	try :
		stdin,stdout,stderr = ssh.exec_command(command)
		result_list=stdout.readlines()
		print (result_list)
	except UnicodeDecodeError as e:
		result_list=stdout.read()
		#result_list=unicode(result_list,'gbk')
		#result_list=filter(lambda x : int(re.findall(__PATTERN_ICS,x)[0])> __MIN_DUR,result_list.split('\n'))
		for x in result_list.split('\n') :
			#print(x)
			print(re.findall(__PATTERN_ICS,x))
	except Exception as e :
		print(e)	

def get_database(ip,user_name,path,frame):
	try :
		ssh=get_connect(ip,user_name)
		if frame == 'ics' :
			log_path=os.path.join(path,cur_date[6:])
			file_name='database*.trc'
			ics_database(ssh,log_path,file_name)
	except Exception as e :
		print(e)

def main():
	pcluter=''
	try :
		pcluter=sys.argv[1]
		#tx_name=sys.argv[2]
	except IndexError :
		config.enum_cluter(file_path)
	try:
		min_dur=int(sys.argv[2])
	except IndexError as e:
		min_dur=__MIN_DUR 
	ip_info=config.read_by_cluter(pcluter)
	if pcluter:
		for each in ip_info :
			ip=each.split(',')[1]
			user_name=each.split(',')[2]
			path=each.split(',')[3]
			frame=each.split(',')[4].replace('\n','')
			get_database(ip,user_name,path,frame)
				
if __name__=='__main__':
	main()