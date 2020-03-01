# -*- coding:utf-8 -*-
import paramiko
from ser_tools.Tools import readFile,chkTools
import datetime
import os,sys
import re
from conf import settings
import threading

rlock=threading.RLock()
__MIN_DUR=settings.MIN_DURATION  # 设置执行时长阀值
file_path=settings.IPLIST_PATH
config=readFile(file_path)
check_tools = chkTools()
cur_date = datetime.datetime.now().strftime('%Y%m%d')
__PATTERN=r'\"dur\":(.*?)\,'

def query_ntp(ssh,log_path,file_name,tx_name,min_dur,ip) :
	
	def get_file_name(ssh,file_name):
		'''找到新框架日志中不包含日期的txnPlt日志'''
		command='cd '+log_path+';ls '+file_name+'|grep -v "[0-9]"'
		stdin,stdout,stderr=ssh.exec_command(command)
		result=stdout.read()
		return result
		
	real_file_name=get_file_name(ssh,file_name)
	command='cd '+log_path+'; grep \'"tc":"'+tx_name+'"\' '+real_file_name
	stdin,stdout,stderr=ssh.exec_command(command)
	rlock.acquire()
	result_list=stdout.readlines()
	result_list=filter(lambda x:int(re.findall(__PATTERN,x)[0]) > min_dur,result_list)
	print('='*8+ip+'='*8)
	print (''.join(map(lambda x:str(x),result_list)))
	rlock.release()
	
def query_ics(ssh,log_path,file_name,tx_name,min_dur,ip):
	if log_path and file_name :
		
		command='cd '+log_path+'; grep \'"tc":"'+tx_name+'"\' '+file_name
		stdin,stdout,stderr=ssh.exec_command(command)
		result_list=stdout.readlines()
		#result_list=result_format(result_list)#日志格式整理
		rlock.acquire()
		result_list=filter(lambda x:int(re.findall(__PATTERN,x)[0]) > min_dur,result_list)
		print('='*8+ip+'='*8)
		print (''.join(map(lambda x:str(x),result_list)))
		rlock.release()
		
def get_tx(ip,user_name,path,frame,tx_name,min_dur):
	'''获取执行时长交易码'''
	#print('='*8+ip+'='*8)
	ssh=get_connect(ip,user_name)
	try :
		if frame== 'ics' :
			log_path=os.path.join(path,cur_date[6:]) #设置查询日志的路径
			file_name='TXNPLT*.lst' #查询日志名
			query_ics(ssh,log_path,file_name,tx_name,min_dur,ip)
		elif frame == 'lemon' :
			log_path=path
			file_name='txnPlte*.log'
			query_ntp(ssh,log_path,file_name,tx_name,min_dur,ip)
	except Exception as e :
		print (e)
	finally :
		ssh.close()
	
def get_connect(ip, user_name):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(ip, 22, user_name, timeout=2.5)
	except Exception as e :
		print (e)
	return ssh


def result_format(result_list):
	'''日志结果整理格式'''
	'''返回结果中的值转换为字典dict'''
	if not result_list :
		return
	#字符串转字典要用eval()
	return map(lambda x:eval(x[x.find('{'):x.find('}')+1].replace('\n','')),result_list)


def main():
	pcluter=''
	try :
		pcluter=sys.argv[1]
		tx_name=sys.argv[2]
	except IndexError :
		print ('\033[1;31;40m %s \033[0m'%"format : sh get_duration 集群名 实例名")
		config.enum_cluter(file_path)
	try :
		min_dur=int(sys.argv[3]) #设置执行时长阀值
	except IndexError as e:
		min_dur=__MIN_DUR  #如果没有输入则是固定值
	ip_info=config.read_by_cluter(pcluter)
	if pcluter:
		for each in ip_info :
			ip=each.split(',')[1]
			user_name=each.split(',')[2]
			path=each.split(',')[3]
			frame=each.split(',')[4].replace('\n','')
			t=threading.Thread(target=get_tx,args=(ip,user_name,path,frame,tx_name,min_dur))
			t.start()
				
if __name__=='__main__':
	main()