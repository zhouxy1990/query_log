# -*- coding:utf-8 -*-
# author : zhou xy


from Commands import command
from ser_tools.param_ssh import sshConnection
from conf import settings
import os
import re
class logQuery(object):
	
	def __init__(self,arg_managment,infos,query_path=None,):
		self.arg_managment=arg_managment
		self._infos = infos
		self._query_path = query_path
		self._log_file = arg_managment.log_file
		self._extra_args = None	
		
	def get_log (self,is_gz):
		'''
		获取日志文件信息
		'''
		comm = command.query_log(self.arg_managment,self._query_path,is_gz)
		stdin,stdout,stderr=sshConnection.exec_command(
			self._infos["ip"],
			self._infos["username"],
			comm
		)
		result = stdout.read()
		return result
	
	def get_file_list(self):	
		'''
		获取日志文件列表
		'''
		query_info = self.arg_managment.query_info
		comm = command.fetch_file(self._query_path,self._log_file)
		stdin,stdout,stderr=sshConnection.exec_command(self._infos["ip"],self._infos["username"],comm)
		file_list = stdout.readlines()
		return file_list
	
	def get_active(self,log_list,th_count=None):
		'''
		获取线程数
		'''
		
		res_list=[]
		for fi in log_list :
			comm = command.get_active(fi,self._query_path,self._infos)
			stdin,stdout,stderr=sshConnection.exec_command(self._infos["ip"],self._infos["username"],comm)
			result=stdout.readlines()
			if self._infos.get("frame") == "ics" :
				pattern = settings.PATTERN_ICS
				if th_count :
					thread_count=int(th_count)
				else :
					thread_count = settings.ICS_MIN_THREAD_COUNT
			else :
				pattern = settings.PATTERN_NTP
				if th_count :
					thread_count=int(th_count)
				else :
					thread_count = settings.NTP_MIN_THREAD_COUNT
			result_list=filter(lambda x : int (re.findall(pattern,x)[0])>= thread_count,result)
			if not result_list:continue
			res_list.extend(result_list)
		if not res_list : return
		res_list=sorted(res_list,key=lambda x : re.findall(pattern,x)[0],reverse=True)
		sorted_list=[item for num,item in enumerate(res_list) if num <= settings.ACTIVE_QUERY_NUM ]
		if self._infos.get("frame") == 'lemon':
			sorted_list = [x.split('- {')[0]+'\n' for x in sorted_list]
		print("".join(sorted_list))
		
		
	@property
	def extra_args(self):
		return self._extra_args
		
	@extra_args.setter
	def extra_args(self,value):
		self._extra_args = value
		
	
	@property	
	def query_path(self):
		return self._query_path
		
		
	@query_path.setter
	def query_path(self,value):
		self._query_path = value
	
	@property
	def log_file(self):
		return self._log_file
		
	@log_file.setter
	def log_file(self,value):
		self._log_file = value