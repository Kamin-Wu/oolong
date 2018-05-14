#-*-coding:utf-8-*-

import json
import re
import smtplib
import SocketServer
import socket
from email.mime.text import MIMEText
from email.Utils import formatdate
from pymongo import MongoClient


######################################################################
#使用Oolong_mail类发送邮件的使用示例：
#mail = Oolong_mail('1037031674@qq.com', 'evoacfuwgmwlbcab', 'smtp.qq.com', 465)
#mail.send_mail(u'主题', u'正文', 'm18813292861@163.com')
class Oolong_mail():
    
    """
    邮件类，专门用于发送邮件
    """

    def __init__(self, user, password, smtp_server, smtp_port=25):
        self.__smtp_server = smtp_server
        self.__smtp_port = smtp_port
        self.__user = user
        self.__password = password
        self.__server = None
        self.login()
    
    def __del__(self):
        self.__server.close()


    def login(self):
        if self.__smtp_port == 25:
            self.__server = smtplib.SMTP(self.__smtp_server, self.__smtp_port)
        else:
            self.__server = smtplib.SMTP_SSL(self.__smtp_server, self.__smtp_port)

        self.__server.login(self.__user, self.__password)
            

    def send_mail(self, subject, content, to_addr, from_addr=None):
        if from_addr == None:
            from_addr = self.__user
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = from_addr
        message['To'] = to_addr
        #message['Subject'] = unicode(subject, 'utf8')
        message['Subject'] = subject
        message['Data'] = formatdate(localtime=True)
        self.__server.sendmail(from_addr, [to_addr], message.as_string())


######################################################################
#使用Conf_resolver类解析配置文件的使用示例：
#conf = Conf_resolver('./oolongd.conf')
#conf_info = conf.conf_info
class Conf_resolver():

    """
    一个日志解析器
    """
    
    def __init__(self, conf_file, symbol = r'#'):
        self.conf_file = conf_file
        self.symbol = symbol
        self.content = ''
        self.__remove_annotation()
        self.conf_info = self.__get_conf_info()
        pass


    def __remove_annotation(self):

        """
        读取配置文件，并删除其中的注释，
        将删除后得到的配置文件内容赋值给实例变量self.content,
        同时将self.content作为该方法的返回值
        """

        re_expression = self.symbol + r'.*'
        with open(self.conf_file, 'r') as f:
            for line in f.readlines():
                line = re.sub(re_expression, r'', line)
                self.content += line
        return self.content


    def __get_conf_info(self):

        """
        将self.content转换为包含配置文件信息的字典
        """

        return eval(self.content)


######################################################################
#通过给Alarm类添加特定的告警模式方法，可实现不同的告警模式
#使用Alarm类进行告警的使用示例：
#alarm = Alarm(conf_info, trigger_info, gather_value)
#alarm.alarm()
class Alarm():
    
    """
    一个告警器，用于发送告警，
    告警方式多样，且可自定义
    """

    def __init__(self, conf_info, trigger_info, gather_value):
        self.conf_info = conf_info
        self.trigger_info = trigger_info
        self.gather_value = gather_value
        pass
    
    def alarm(self):
        trigger_mode = self.trigger_info['trigger_mode']
        alarm_mode = self.trigger_info[trigger_mode]['alarm_mode']
        if hasattr(self, alarm_mode):
            alarm_func = getattr(self, alarm_mode)
            alarm_func()
        else:
            print("Can't find the alarm_mode:%s"%alarm_mode)
        
    def email_alarm(self):
        user = self.conf_info['email_user']
        password = self.conf_info['email_pw']
        trigger_mode = self.trigger_info['trigger_mode']
        to_email = self.trigger_info[trigger_mode]['email_alarm']['to']
        smtp_server = self.conf_info['smtp_server']
        smtp_port = self.conf_info['smtp_port']

        title = u"THE ALARM FROM OOLONG MONITORING SYSTEM"
        content = u"""
        The %(MI)s's value is %(gather_value)d
        It's %(state)s the threshold %(threshold)s.
        """ %{'MI':self.trigger_info['_id'], 
            'gather_value':self.gather_value, 
            'state':self.trigger_info[trigger_mode]['compare'], 
            'threshold':self.trigger_info[trigger_mode]['threshold']}

        mail = Oolong_mail(user, password, smtp_server, smtp_port)
        #mail.send_mail(u'主题', u'正文', 'm18813292861@163.com')
        mail.send_mail(title, content, to_email)
        print("This is a email alarm")


######################################################################
#使用Event类进行告警的使用示例：
#
#
class Event():

    """
    当触发器判定采集的数据异常后，就会生成一个event对象，
    用于处理异常，发送告警
    """

    def __init__(self, conf_info, trigger_info, gather_value):
        self.conf_info = conf_info
        self.trigger_info = trigger_info
        self.gather_value = gather_value
        self.event_info = self.__get_event_info()
        self.alarm_state = True
    
    def __get_event_info(self):
        conn = MongoClient(self.conf_info['mongodb_host'], self.conf_info['mongodb_port'])
        collection = conn.oolong.event
        event_info = collection.find_one({'_id':self.trigger_info['_id']})
        return event_info

    def active(self):
        if self.event_info['auto_script']:
            self.active_auto_script()
        if self.event_info['alarm']:
            self.active_alarm()

    def active_auto_script(self):
        pass

    def active_alarm(self):
        if self.alarm_state == True:
            alarm = Alarm(self.conf_info, self.trigger_info, self.gather_value)
            alarm.alarm()



######################################################################
#使用Trigger类进行告警的使用示例：
#trigger = Trigger(conf_info)
#res = trigger.judge(judged_data)
#其中，judge_data为一个键值对，key为监控项，value为采集值；
#res为True表示采集数据触发判定条件。
class Trigger():
    
    """
    一个触发器，用于判定采集的数据是否触发告警
    """

    def __init__(self, conf_info):
        self.conf_info = conf_info
        self.oolong_db = self.__get_oolong_db()
        pass
    
    def __get_oolong_db(self):
        mongodb_host = self.conf_info['mongodb_host']
        mongodb_port = self.conf_info['mongodb_port']

        conn = MongoClient(mongodb_host, mongodb_port)
        db = conn.oolong
        return db
    
        

    def judge(self, judged_data):

        """
        根据judge_data，从oolong数据库中的trigger集合中读取其触发
        方式和触发条件，并进行判定。
        满足触发条件则返回True，否则返回False
        """
        
        timestamp = judged_data.pop('_id')
        key = judged_data.keys()[0]
        print "key:", key
        value = judged_data.values()[0]
        trigger_info = self.oolong_db.trigger.find_one({'_id':key})
        print "触发器信息：",trigger_info
        if trigger_info == None:
            print("为在数据库中为%(key)s配置触发器信息。"%{'key':key})
            judge_result = False
            return judge_result,trigger_info
        trigger_mode = trigger_info['trigger_mode']
        trigger_conf = trigger_info[trigger_mode]
        print trigger_conf
        if hasattr(self, trigger_mode):
            judge_func = getattr(self, trigger_mode)
            judge_result = judge_func(key, value, trigger_conf)
            return judge_result,trigger_info
        else:
            print("未找到此告警模式函数：", trigger_mode)
        

    def fixed_threshold(self, key, value, trigger_conf):
        threshold = trigger_conf['threshold']
        compare =   trigger_conf['compare']
        alarm_mode = trigger_conf['alarm_mode']

        cmp_result = cmp(value,threshold)
        if cmp_result == -1:
            cmp_result = 'under_threshold'
        elif cmp_result == 0 or cmp_result == 1:
            cmp_result = 'over_threshold'
        
        if cmp_result == compare:
            return True
        else:
            return False

    def other_trigger_mode():
        """

        """
        pass


#############################################
#
#
#
class MyTCPHandler(SocketServer.BaseRequestHandler):

    """
    TCPSocket控制器
    """

    def handle(self):

        """
        监听的套接字接收到数据后，将会执行此方法
        """

        print("进入Hander函数")
        while True:
            self.data = self.request.recv(10240).strip()
            if not self.data:
                print(self.client_address, "down.")
                break
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
            judged_data_list = eval(self.data)
            for judged_data in judged_data_list:
                print "judged_data:",judged_data
                judge_result, trigger_info = trigger.judge(judged_data)
                if judge_result:
                    event = Event(conf_info, trigger_info, judged_data.values()[0])
                    print("created event")
                    event.active()


def main():
   
    global conf
    conf = Conf_resolver('./oolongd.conf')
    global conf_info
    conf_info = conf.conf_info
    global trigger
    trigger = Trigger(conf_info)    
    server = SocketServer.ThreadingTCPServer((conf_info['server_host'], conf_info['server_port']), MyTCPHandler)
    print"启动监听"
    server.serve_forever()
    print"监听结束"


if __name__ == "__main__":
    main()
