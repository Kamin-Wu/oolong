#-*-coding:utf-8-*-

from pymongo import MongoClient
import time
import re


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
 

def get_time_stamp():
    time_str = time.strftime('%Y-%m-%d-%H-%M')
    time_struct = time.strptime(time_str, '%Y-%m-%d-%H-%M')
    time_stamp = time.mktime(time_struct)
    time_stamp = int(time_stamp)
    return time_stamp
