# -*- coding:utf-8 -*-
# author : zhou xy


import os
class readFile(object):

	def __init__(self,file_path):

		self.file_path=file_path


	
	def cluster_split(func):
		def inner(self,pcluster,*agrs,**kwages):
			if "," in pcluster :
				pclusters = pcluster.split(",")
				ip_infos=[]
				for p in pclusters :
					ip_info=func(self,p)
					ip_infos.extend(ip_info)
				return ip_infos
			else :
				return func(self,pcluster)
		return inner
		
	
	def cluster_split_show(func):
		def inner(cls,file_path,node,*agrs,**kwages):
			if "," in node :
				nodes = node.split(",")
				ip_infos=[]
				for n in nodes :
					ip_info=func(cls,file_path,n)
					ip_infos.append(ip_info)
				return ip_infos
			else :
				return func(cls,file_path,node)
		return inner
	
	@cluster_split
	def read_by_cluter(self,pcluster):
		ip_info=[]
		with open(self.file_path) as file :
			lines=file.readlines()
		if pcluster :	
			ip_info=filter(lambda x:pcluster==x.split(',')[0] or pcluster==x.split(',')[1],lines)
			if ip_info==[] :
				print ('输入的{}不存在'.format(pcluster))
		return ip_info

	def query_cluter(self) :
		with open(self.file_path) as file :
			lines=file.readlines()
		return map(lambda x :x.split(',')[0],lines)
	
	
	def query_redis_cluter(self,p_app_id):
		redis_info=[]
		with open(self.file_path) as file :
			lines=file.readlines()
		if p_app_id  :
			redis_info=filter(lambda x:x.split(',')[0]==p_app_id ,lines)	
		return redis_info

	def query_redis_info(self):
		'''
		查询redis信息
		'''
		with open(self.file_path) as file :
			lines=file.readlines()
		return lines

	@classmethod
	def enum_cluter(cls,file_path) :
		'''
		枚举集群信息
		'''	
		ip_info=cls(file_path).query_cluter()
		ip_info=set(ip_info)
		print ('请输入集群或者IP')
		print ('cluter :')
		print (" , ".join(ip_info))

	def query_cluter_info(self):
		'''
		查看集群信息
		取iplist中ip和解释
		'''
		cluters=[]
		with open(self.file_path) as file :
			lines=file.readlines()
		return map(lambda x :(x.split(',')[0],x.split(',')[5]),lines)
	
		 
	
	@classmethod
	def show_cluter_info(cls,file_path):
		'''
		查看集群简介 -h
		'''
		cluter_info = cls(file_path).query_cluter_info()
		cluter_info = list(set(cluter_info))
		cluter_info = sorted(cluter_info,key=lambda x : x[0])#按字母排序
		times=1
		for cluter,info in cluter_info :
			info=info.replace('\n','')
			if len(cluter) <= 15 :
				cluter=cluter.ljust(15)
			if len(info) <= 19 :
				info=info.ljust(19)
			if times % 5 == 0 :
				print (cluter+'==>'+'\033[1;31;40m%s\033[0m'%info+'|')
			else :
				print (cluter+'==>'+'\033[1;31;40m%s\033[0m'%info+'|'), #结尾加逗号不换行输出
			times+=1
	
	@classmethod	
	@cluster_split_show	
	def show_detail_info(cls,file_path,node):
		'''
		集群机器配置信息 -info
		'''
		import json
		ip_info = cls(file_path).read_by_cluter(node)		
		ips = [info.split(",")[1] for info in ip_info]
		cluter = {info.split(",")[0] for info in ip_info}
		detail_info = {c : ips for c in cluter}	
		detail_info = json.dumps(detail_info,indent=4)
		print(detail_info)
			
		
class chkTools(object) :

	def chk_files(func):
		def inner(self,files,*args,**kwargs):
			if isinstance(files,list):
				return func(self,files)
			elif isinstance(files,str) :
				if files.endswith('.gz') : return True
				else : return False
		return inner

	def filter_log_time(self,file_list,log_dt):
		import time
		log_list=[]
		#年份不影响日期查询
		time_string='2019-{}-{} 00:00:00'.format(log_dt[:2],log_dt[2:])
		asc_time=time.asctime(time.strptime(time_string,'%Y-%m-%d %H:%M:%S')).split()
		if file_list :
			file_list=filter(lambda x : x.split()[5]==log_dt[:2] or x.split()[5]==asc_time[1] ,file_list)
			log_list=[x.split()[8] for x in file_list]
		return log_list

	@chk_files
	def chk_is_gz(self,files) :
		is_gz=False
		for each in files :
			if each.endswith('.gz') :
				is_gz=True
				break
		return is_gz

	@staticmethod
	def remove_all(path):
		import os
		os.chdir(path)
		file_list=os.listdir(path)
		for file in file_list :
			file_path=os.path.join(path,file)
			os.remove(file_path)




class IOOperation(object):
	
	def __init__(self,file_path):
		self.file_path=file_path

	def write_file(self,string,ip,log_name,date):
		path=os.path.join(self.file_path,'chk_'+date+'.txt')

		if not os.path.exists(path) :
			with open (path,'w') as f :
				f.write(string+'\n')
		else :
			with open (path,'a+') as f :
				f.write(string+'\n')