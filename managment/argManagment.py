# -*- coding:utf-8 -*-
# author : zhou xy

from ser_tools.Tools import readFile
from conf import settings
FILE_PATH = settings.IPLIST_PATH
config=readFile(FILE_PATH)



class argManager(object):
	
	def __init__(self,cluster=None,log_dt=None,key_word=None,log_file=None,ser_name=None,extr_agrs=None	):
		self._cluster = cluster
		self._log_dt = log_dt
		self._key_word = key_word
		self._log_file = log_file
		self._extr_agrs = extr_agrs
		self._ser_name = ser_name
		self._query_info = {}
		
	@property
	def query_info(self):
		ip_info=config.read_by_cluter(self._cluster)
		tmp_list=[]
		for info in ip_info :
			tmp_dict={}
			cluster = info.split(",")[0]
			ip = info.split(",")[1]
			username = info.split(",")[2]
			log_path = info.split(",")[3]
			frame = info.split(",")[4]
			explain = info.split(",")[5]
			tmp_dict={"cluster" : cluster,
								"ip" :ip,
								"username" : username,
								"log_path" : log_path ,
								"frame" : frame,
								"explain"  : explain
								}
			tmp_list.append(tmp_dict)
		self._query_info = {self._cluster : tmp_list}	
		return self._query_info
	
	#@query_info.setter	
	#def set_query_info(self,k,v):
	#	self.query_info={k,v}
		
		
	@property	
	def cluster(self):
		return self._cluster
	
	@cluster.getter
	def cluster(self):
		return self._cluster		
	
	@cluster.setter		
	def cluster(self,value):
		self._cluster = value
		
		
	@property	
	def log_dt(self):
		return self._log_dt
	
	@log_dt.getter
	def log_dt(self):
		return self._log_dt		
	
	@log_dt.setter		
	def log_dt(self,value):
		self._log_dt = value
	
		
	@property	
	def key_word(self):
		return self._key_word
	
	@key_word.getter
	def key_word(self):
		return self._key_word	
		
	@property	
	def log_file(self):
		return self._log_file
	
	'''
	@log_file.setter
	def set_log_file(self,value):
		self._log_file = value
	'''
		
	@property
	def extr_agrs(self):
		return self._extr_agrs
		
	@extr_agrs.getter
	def get_log_dt(self):
		return self._extr_agrs		
	
	@extr_agrs.setter		
	def set_extr_agrs(self,value):
		self._extr_agrs = value
		
	@property	
	def ser_name(self):
		return self._ser_name
		
	@ser_name.setter
	def set_ser_name(self,value):
		self._ser_name = value