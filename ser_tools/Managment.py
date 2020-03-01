# -*- coding:utf-8 -*-
# author : zhou xy

import argparse
import sys
from ser_tools.Tools import readFile
from conf import settings 
FILE_PATH=settings.IPLIST_PATH
config=readFile(FILE_PATH)
class Args (object) :
	
	def __init__(self,):
		self.parse = argparse.ArgumentParser()
		
	def add_arg(self,arg_name,help_inf=None):
		self.parse.add_argument(arg_name,help=help_inf)
		args = self.parse.parse_args()
		return args
		
	@classmethod
	def get_arg(cls,arg_name,help_inf=None):
		args = cls().add_arg(arg_name,help_inf)
		if hasattr(args,arg_name.replace('-','')) and getattr(args,arg_name.replace('-','')) :
			pass
			
			
HELP_INFO="输入集群查看集群中的IP或者输入IP查看该IP归属集群"
			
def parse_args(pcluter):
	args = Args()
	if pcluter == '-info' :
		arg = args.add_arg(pcluter,help_inf=HELP_INFO)
		if hasattr(arg,pcluter.replace('-','')):	
			info = getattr(arg,pcluter.replace('-',''))
			detail_info = config.show_detail_info(settings.IPLIST_PATH,info)
			sys.exit()
	if pcluter == '-h' or pcluter == '-H' or pcluter == 'help' :
		config.show_cluter_info(FILE_PATH)
		sys.exit()