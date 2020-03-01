# -*- coding:utf-8 --

import sys
import traceback
import paramiko
import socket
class sshConnection(object) :
	
	def __init__(self,ip,user_name,port=22,password=None):
		self._ip =ip
		self._user_name=user_name
		self._port = port
		self._password = password
		self.ssh = None
		
	def get_conn(self):
		try :
			self.ssh=paramiko.SSHClient()
			self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self._password :
				self.ssh.connect(self._ip,self._port,self._user_name,self._password,timeout=2.5)
				return self.ssh
			self.ssh.connect(self._ip,self._port,self._user_name,timeout=2.5)
			return self.ssh 
		
		except socket.error as e:
			print ('='*8+self._ip+'='*8)
			print (e)
			sys.exit()
			
		except Exception as e:
			print ('='*8+self._ip+'='*8)
			print(e)
			#traceback.print_exc()
			sys.exit()
			
			
	@classmethod
	def exec_command(cls,ip,user_name,command):
		conn = cls(ip,user_name)
		ssh = conn.get_conn()
		try :
			
			stdin,stdout,stderr=ssh.exec_command(command)
			return stdin,stdout,stderr
			
		except Exception as e  :
			print (e)	
			conn.close_conn()
			
			
	def close_conn(self):
		if self.ssh :
			self.ssh.close()