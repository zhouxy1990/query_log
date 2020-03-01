# -*- coding:utf-8 -*-
import os
from Tools import IOOperation

class SSH_Operation(object):

	def __init__(self,ssh):
		self.ssh=ssh

	def get_log_file(self,query_path,log_file=None):
		if log_file :
			stdin,stdout,stderr=self.ssh.exec_command('cd {} ;ls -lrt {}*'.format(query_path,log_file))
		else :	
			stdin,stdout,stderr=self.ssh.exec_command('cd {} ;ls -lrt '.format(query_path))
		return stdout.readlines()
	
	
		

	def find_error0(self,log_file,path):
		
		def split_line(error_line):
			error_lines=error_line.split(':')
			try :
				return ':'.join([error_lines[0],error_lines[1]])
			except IndexError :
				return error_lines
			
		try:#Exception日志除去IllegalStateException
			command="cd {} ;fgrep Exception {}".format(path,log_file)
			stdin,stdout,stderr=self.ssh.exec_command(command)
			error_list=stdout.readlines()
			if not error_list :
				return
			error_list=filter(lambda x: x.startswith('java'),error_list)#取java开头的 Execption错误
			error_list=filter(lambda x: 'IllegalStateException' not in x ,error_list)
			error_list=map(split_line ,error_list)
			if not error_list :
				return
			error_list=[x for x in set(error_list)]#对错误进行去重
		except UnicodeDecodeError:
			try:
				error_list=[]
				sftp_client=self.ssh.open_sftp()
				files=sftp_client.open(os.path.join(path,log_file),'rb')
				for lines in files :
					if 'Exception' in lines and lines.startswith('java') :
						error_list.append(lines)
				error_list=map(split_line ,error_list)
				if not error_list :
					return
				error_list=[x for x in set(error_list)]
	#			error_list=map(lambda x:x.split(':')[0]+':'+x.split(':')[1],error_list)
				error_list=filter(lambda x: 'IllegalStateException' not in x ,error_list)
				return error_list
			except TypeError :
				return 
			except Exception :
				return 
		except TypeError :
			return
		except Exception :
			return None

	def find_error1(self,log_file,path):
		try :#交易不存在
			command='cd {} ;grep 213303:213303 {}'.format(path,log_file)
			stdin,stdout,stderr=self.ssh.exec_command(command)
			error_list=stdout.readlines()
			if not error_list :
				return None
			error_list=filter(lambda x: x.startswith('213303:213303'),error_list)
			if not error_list :
				return None
			error_list=list(set(error_list))
			error_list=map(lambda x:x.split('[')[0]+'.*'+x.split('[')[1] ,error_list)
		except UnicodeDecodeError :
			error_list=[]
			sftp_client=self.ssh.open_sftp()
			files=sftp_client.open(os.path.join(path,log_file),'rb')
			for lines in files :
				if '213303:213303' in lines and lines.x.startswith('213303:213303') :
					error_list.append(lines)
			if not error_list :
				return None
			error_list=[set(error_list)]
			error_list=map(lambda x:x.split('[')[0]+'.*'+x.split('[')[1] ,error_list)
			return error_list
		except Exception :
			return 
		return error_list

	def find_error2(self, log_file, path) :
		try:#IllegalStateException报错日志
			command = 'cd {} ;fgrep IllegalStateException {}'.format(path, log_file)
			stdin, stdout, stderr = self.ssh.exec_command(command)
			error_list = stdout.readlines()
			error_list = filter(lambda x: x.startswith('java'), error_list)  
			error_list= map(lambda x:x.split(':')[0],error_list)
			if not error_list :
				return
			error_list = list(set(error_list))
		except UnicodeDecodeError:
			error_list = []
			sftp_client = self.ssh.open_sftp()
			files = sftp_client.open(os.path.join(path, log_file), 'rb')
			for lines in files:
				if 'IllegalStateException' in lines and lines.startswith('java'):
					error_list.append(lines)
			error_list= map(lambda x:x.split(':')[0],error_list)
			if not error_list :
				return
			error_list = list(set(error_list))
			return error_list
		except Exception as e :
			print (e)
			return None
		return  error_list

	def find_error3(self, log_file, path) :
		try:#交易码
			command = "cd {} ;grep -Po '<TX_CD>(.*?)</TX_CD>' {}".format(path, log_file)
			stdin, stdout, stderr = self.ssh.exec_command(command)
			error_list = stdout.readlines()
			error_list = list(set(error_list))
		except Exception as e:
			print (e)
			return None
		return error_list

	def sftp_download(self,sftp_path,local_path):
		try :
			sftp=self.ssh.open_sftp()
			sftp.get(sftp_path,local_path)
		except Exception as e:
			print (e)
		
	@staticmethod
	def check_error_file(log_list,last_log_list):
		check_list=[]
		for num,cur_log in enumerate(log_list) :
			if not cur_log.endswith('log'):
				continue
			for last_log in last_log_list :
				if cur_log in last_log :
					break
			else:
				check_list.append(cur_log)
				del log_list[num]
		return check_list
	
	@staticmethod	
	def compare_log(error_list,local_file,log_file,ip,result_path,cur_date):
		import re
		import gzip
		import traceback
		ioo=IOOperation(result_path)
		try:
			error_flg=False
			if local_file.endswith('.gz'):
				for error in error_list :
					with gzip.open(local_file,'r') as f :
						text=f.read()
					result=re.findall(error.replace('\n',''),text)
					if result :
						error_flg=True
						#print ('{}日志{}无新增报错{}'.format(ip,log_file,error))
						continue
					else :
						write_file=ioo.write_file('{}日志{}有新增报错,关键字：{}'.format(ip,log_file,error),ip,log_file,cur_date)
						print ('{}日志{}有新增报错,关键字：{}'.format(ip,log_file,error))
			else :
				for error in error_list :
					with open(local_file,'r') as f :
						text=f.read()
					result=re.findall(error,text)
					if result :
						error_flg=True
						#print ('{}日志{}无新增报错{}'.format(ip,log_file,error))
						continue
					else :
						write_file=ioo.write_file('{}日志{}有新增报错,关键字：{}'.format(ip,log_file,error),ip,log_file,cur_date)
						print ('{}日志{}有新增报错,关键字：{}'.format(ip,log_file,error))
			
		except Exception as e :
			print (e)
			traceback.print_exc()
