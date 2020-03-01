# -*- coding:utf-8 -*-
import sys
from Tools import readFile
from Tools import chkTools
import paramiko
import json
import re
import time
''' python 2.7 '''

'''
只查询TXNPLTE_*.lst
'''

date=time.strftime('%Y%m%d',time.localtime(time.time())) #当前时间

reload(sys)
sys.setdefaultencoding('gbk')

file_path='../iplist_new.lst'
config=readFile(file_path)
check_tools=chkTools()

def filter_digit(log_list):
	log_filter_list=[]
	for each in log_list :
		file_name=each.replace('-','').replace('.','')
		if file_name.isalpha() :
			log_filter_list.append(each)

	return log_filter_list

def sort_duration(sort_list,number):
	sorted_list=[]
	sort_json=sorted(sort_list,key=lambda x : x['dur'],reverse=True)
	for num,item in enumerate(sort_json) :
		if num < int(number) :
			sorted_list.append(item)
		else :
			break
	return sorted_list

def get_dur(ip,user_name,path,frame,log_dt,number):

	try :
		file_list=[]
		log_list=[]
		json_list=[]
		tmp_list=[]
#		paramiko.util.log_to_file("paramiko.log")
		ssh=paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(ip,22,user_name)
		if frame=='ics' :
			file_path=path+'/'+log_dt[2:]
			stdin,stdout,stderr=ssh.exec_command('cd '+file_path+' ;ls -lrt TXNPLTE_*.lst')
			file_list=stdout.readlines()
			log_list=check_tools.filter_log_time(file_list,log_dt)
		elif frame=='ntp' :
			file_path=path
			stdin,stdout,stderr=ssh.exec_command('cd '+path+' ;ls -lrt txnPlte-*.log')
			file_list=stdout.readlines()
			log_list=check_tools.filter_log_time(file_list,log_dt)		
			log_list=filter_digit(log_list)
#		print(log_list)
		if log_list :
			for each in log_list :
				sftp_client=ssh.open_sftp()
				files=sftp_client.open(file_path+'/'+each,'rb')
				for lines in files :
					line=lines[lines.find('{'):lines.find('}')+1].replace('\n','')
					data=json.loads(line)
					json_list.append(data)
				tmp_list.extend(json_list)
			return sort_duration(json_list,number)
		else :
			return None
#			return None
#		ssh.sftp_client.open()
	except Exception as e:
		print (e)
	finally :
		ssh.close()


def main():	
	try :
		ip_info=config.query_cluter()
		ip_info=set(ip_info)
		total_list=[]
		total_sorted_list=[]
		while True :
			pcluter=raw_input("请输入集群或者IP  (PAY or 172.16.6.38):").upper()
			if not re.match(r'^[A-Z]+$',pcluter) \
			and not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",pcluter) :
				print ("请输入正确的集群名或者IP")
				ip_info=config.query_cluter()
				ip_info=set(ip_info)
				print (" , ".join(ip_info))
				continue
			else :
				break

		while True :
			try :
				number=input("请输入Top数 :")
			except NameError as e:
				print (e,'请输入数字')
				continue
			else :
				if type(number)==int and number>0 :	
					break
				else :
					print ("请输入大于0的整数")
					continue

		log_dt=date[4:]
#		log_dt=raw_input("input a time  (0101):")
#		pcluter=sys.argv[1]
#		log_dt=sys.argv[2]
	except IndexError :
		ip_info=config.query_cluter()
		ip_info=set(ip_info)
		print ('请输入集群或者IP ')
		print ('集群名 :')
		print (" , ".join(ip_info))
	

	else :	
		if re.match(r'^[A-Z]+$',pcluter) :
			ip_info=config.read_by_cluter(pcluter)
		elif re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",pcluter) :
			ip_info=config.read_by_cluter(pcluter)
		for each in ip_info :
				cluter=each.split(',')[0]
				ip=each.split(',')[1]
				user_name=each.split(',')[2]
				path=each.split(',')[3]
				frame=each.split(',')[4].replace('\n','')
				sorted_list=get_dur(ip,user_name,path,frame,log_dt,number)
				if sorted_list:
					total_list.extend(sorted_list)
		sort_total_list=sort_duration(total_list,number)
#		print (sort_total_list)
		for num,each in enumerate(sort_total_list) :
			print ('Top{} --msg_id:{} ,reg_id:{} ,nod : {} ,tx_cd :{} ,start_time :{} ,duration :{}'.format(\
				str(num+1),each['lsn'],each['reg'],each['nod'],each['tc'],each['st'],each['dur']))
if __name__=='__main__' :
	main()

