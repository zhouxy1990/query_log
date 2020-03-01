# -*- coding:utf-8 -*-
import redis
import sys
from ser_tools.Tools import readFile
import os


FILE_PATH=os.path.join(os.path.dirname(os.path.realpath(__file__)),"conf/redis.lst")
CONFIG=readFile(FILE_PATH)

def test_conn(host,password,port):
	conn_res=False
	command='/usr/local/bin/redis-cli -h {} -p {} -a {} PING'.format(host,port,password)
	res=os.popen(command)
	result=res.read().replace('\n','')

	if 'Authentication' in result :
		print (result)
	if result == 'PONG' :
		conn_res=True
	return conn_res
	
	
def query_redis(r,key):
	r_type=r.type(key)
	if r_type =='hash' :
		print(str(r.hgetall(key)).decode('utf8'))
	elif r_type == 'list':
		#list从左到右取全部
		print(r.lrange(key,0,-1))
	elif r_type == 'string':
		print(r.get(key).decode('utf8'))
	elif r_type=='set' :
		print (r.smembers(key))
	elif r_type=='none':
		return
	else :
		print ('{}类型不正确'.format(r_type))

def conn_redis(host,password,port,key):
	#print (key)
	try :
		pool=redis.ConnectionPool(host=host,password=password,port=port)
		r=redis.Redis(connection_pool=pool)
		query_redis(r,key)
	except redis.exceptions.ResponseError as e :
		if 'MOVED' in str(e):
			'''如果报错数据MOVED，直接跳转登录至迁移的机器'''
			host,port=str(e).split()[2].split(':')
			pool=redis.ConnectionPool(host=host,password=password,port=int(port))
			r=redis.Redis(connection_pool=pool)
			query_redis(r,key)
	except Exception as e :
		print (e)
		return
		
def run():
	try:
		app_id=sys.argv[1]
		key=sys.argv[2]
	except IndexError :
		print ('example : sh conn_redis.sh app_id key')
		print ('\033[1;31;40m %s \033[0m'%'注：如果键值中包含特殊符号，如 | ，请将键值用""包裹')
		rds_info=CONFIG.query_redis_info()
		for each in rds_info :
			r_app_id=each.split(',')[0]
			r_cluter=each.split(',')[1]
			r_explain=each.split(',')[5]+each.split(',')[6].replace('\r','').replace('\n','')
			print ('app_id :{} ,ip :{}, info :{}'.format(r_app_id,r_cluter,r_explain))
	else :
		redis_info=CONFIG.query_redis_cluter(app_id)
		if redis_info :
			for each in redis_info :
				host=each.split(',')[1]
				password=each.split(',')[3]
				port=int(each.split(',')[2])
				if host and password and port:
					print ('='*8+host+'='*8)
					conn_redis(host,password,port,key)
				else : 
					print ('connect failed ')
					continue

#	print (redis_info)
if __name__=='__main__':
	run()