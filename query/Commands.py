# -*- coding:utf-8 -*-
# author : zhou xy



class command(object):
	
	
	@staticmethod	
	def fetch_file(query_path,log_name):
		
		return 'cd '+query_path+' ;ls -lrt '+log_name
	
	@staticmethod
	def query_log(arg_managment,query_path,is_gz):
		key_word = arg_managment.key_word
		log_file = arg_managment.log_file
		if not query_path :
			raise ValueError (" path can not be None ")
		if not is_gz :
			comm= 'cd '+ query_path +' ;fgrep '+key_word+' '+log_file
		else :
			comm = 'cd '+ query_path +' ;zgrep '+key_word+' '+log_file	
		return comm
		
	
	@staticmethod
	def get_active(log_file,log_path,infos):
		if infos.get("frame") == 'ics':
			comm='cd '+log_path+';fgrep activeCount '+log_file
		else :
			comm='cd '+log_path+"; egrep '\]\: \[(.*?)\] \- \{' "+log_file
		return comm