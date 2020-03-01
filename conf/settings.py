# -*- coding:utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


#ip配置文件
IPLIST_PATH=os.path.join(BASE_DIR,'iplist_new.lst') 


#redis配置文件
REDIS_LIST_PATH=os.path.join(BASE_DIR,'redis.lst') 


#ICS查询线程数阈值
ICS_MIN_THREAD_COUNT = 60 


#新框架查询线程数阈值
NTP_MIN_THREAD_COUNT = 60

#线程数查询条数
ACTIVE_QUERY_NUM = 10

#设置执行时长阀值ms
MIN_DURATION = 4000



PATTERN_ICS=r'activeCount:\[(.*?)\]'

PATTERN_NTP=r'\]\: \[(.*?)\] \- \{'

