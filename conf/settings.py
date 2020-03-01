# -*- coding:utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


#ip�����ļ�
IPLIST_PATH=os.path.join(BASE_DIR,'iplist_new.lst') 


#redis�����ļ�
REDIS_LIST_PATH=os.path.join(BASE_DIR,'redis.lst') 


#ICS��ѯ�߳�����ֵ
ICS_MIN_THREAD_COUNT = 60 


#�¿�ܲ�ѯ�߳�����ֵ
NTP_MIN_THREAD_COUNT = 60

#�߳�����ѯ����
ACTIVE_QUERY_NUM = 10

#����ִ��ʱ����ֵms
MIN_DURATION = 4000



PATTERN_ICS=r'activeCount:\[(.*?)\]'

PATTERN_NTP=r'\]\: \[(.*?)\] \- \{'

