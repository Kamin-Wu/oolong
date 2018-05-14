#-*-coding:utf-8-*-

import socket
import psutil
from  common.utils import *


def send_info_to_agent(msg):

    """
    将monitor收集到的信息发送给agent
    """

    client = socket.socket()
    client.connect((conf_info['agent_host'], conf_info['agent_port']))
    client.send(msg)
    print("send:", msg)
    client.close()


def get_info():

    """
    需要根据监控需求自定义的函数，
    用于获取监控数据，并以特定的格式返回
    格式示例：[{'_id':100,'host_cpu_avgtime':100}, {'_id':100,'host_cpu_rate':30}]
    """

    time_stamp = get_time_stamp()
    cpu = psutil.cpu_times()
    cpu_total = cpu.user+cpu.system+cpu.idle
    cpu_busy = cpu.user+cpu.system
    host_cpu_busy = round(cpu_busy/cpu_total*100,2)
    host_cpu_system = round(cpu.system/cpu_total*100,2)
    host_cpu_user = round(cpu.user/cpu_total*100,2)

    info = [
        {'_id':time_stamp, 'host_cpu_busy':host_cpu_busy},
        {'_id':time_stamp, 'host_cpu_system':host_cpu_system},
        {'_id':time_stamp, 'host_cpu_user':host_cpu_user},
    ]
    print info
    return str(info)


def main():
    global conf
    conf = Conf_resolver('./agent.conf')
    global conf_info
    conf_info = conf.conf_info
    send_info_to_agent(get_info())
    print("send over.")
    

if __name__ == '__main__':
    main()
