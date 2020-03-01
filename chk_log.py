# -*- coding:utf-8 -*-
import sys
import os
from Tools import readFile, chkTools
import datetime
import paramiko
from log_service import SSH_Operation
import traceback

BASE_DIR = os.path.realpath(__file__)
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))) \
                         , 'iplist_new.lst')
local_path = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'tmp')
config = readFile(file_path)
check_tools = chkTools()
cur_date = datetime.datetime.now().strftime('%Y%m%d')
last_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y%m%d')
result_path=os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)),'check_log')

def get_connect(ip, user_name):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, 22, user_name, timeout=2.5)
	return ssh


def get_log_list(ssho, query_path, date):
	file_list = ssho.get_log_file(query_path)  # 获取路径下的文件
	if len(file_list) > 1:
		del file_list[0]  # 删除第一个元素
		log_list = check_tools.filter_log_time(file_list, date[4:])
		return log_list
	return None


def fetch_log(ip, user_name, path, frame):
	ssh = get_connect(ip, user_name)
	if frame == 'ics':
		path = path.replace('trc', 'log')
		try:
			ssho = SSH_Operation(ssh)
			query_path = os.path.join(path, cur_date[6:])  # 查询文件路劲
			log_list = get_log_list(ssho, query_path, cur_date)
			if not log_list:return
			last_query_path = os.path.join(path, last_date[6:])  # 查询文件路劲
			last_log_list = get_log_list(ssho, last_query_path, last_date)
			if not last_log_list:return
			print('=' * 5 + ip + '=' * 5)
			check_list = ssho.check_error_file(log_list, last_log_list)
			if check_list:
				print('存在新增日志:{}'.format(' , '.join(check_list)).decode('utf8'))
			for log_file in log_list:
				num = 0
				error_lists = []
				while True:
					if not hasattr(ssho, 'find_error' + str(num)):break
					func_name = getattr(ssho, 'find_error' + str(num))
					num += 1
					error_list = func_name(log_file, query_path)
					if not error_list:continue
					error_lists.append(error_list)
				if not error_lists:continue
				last_query_path = os.path.join(path, last_date[6:])  # 查询文件路劲
				last_file_list = ssho.get_log_file(last_query_path, log_file=log_file)  # 查询前一日的日志文件
				last_log_list = check_tools.filter_log_time(last_file_list, last_date[4:])
				if not last_log_list:continue
            #				ssho.check_error_file(log_list,last_log_list)
				for last_log in last_log_list:
					sftp_file = os.path.join(last_query_path, last_log)
					local_file = os.path.join(local_path, '{}_{}_{}'.format(ip.replace('.', '_'), last_date[4:], last_log))
					ssho.sftp_download(sftp_file, local_file)
					for error_list in error_lists:
						ssho.compare_log(error_list, local_file, log_file, ip,result_path,cur_date)
				print('{}已执行完成'.format(ip).decode('utf8'))
		except ValueError as e:
			print(e)
		except KeyboardInterrupt:
			print('you have stopped the threading...')
		except Exception as e:
			print(e.message)
			traceback.print_exc()
		finally:
			ssh.close()
			check_tools.remove_all(local_path)
	elif frame == 'ntp' :return
    


def main():
    try:
		pcluter = sys.argv[1]

    except IndexError:
		config.enum_cluter(file_path)
    else:
		ip_info = config.read_by_cluter(pcluter)
		if pcluter:
			for each in ip_info:
				cluter = each.split(',')[0]
				ip = each.split(',')[1]
				user_name = each.split(',')[2]
				path = each.split(',')[3]
				frame = each.split(',')[4].replace('\n', '')
				fetch_log(ip, user_name, path, frame)


if __name__ == '__main__':
	main()