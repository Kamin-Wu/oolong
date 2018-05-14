#-*-coding:utf-8-*-

import SocketServer
import socket
from pymongo import MongoClient
from common.utils import *


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

            #向客户端发送消息，以测试是否成功接收
            #self.request.send(self.data.upper())
            #print("send over")

            #向数据节点MongoDB插入数据
            conn = MongoClient(conf_info['mongodb_host'], conf_info['mongodb_port'])
            db = conn.oolong
            collection = db.host
            for i in eval(self.data):
                collection.update(
                    {'_id':i['_id']},
                    {'$set':i},
                    upsert=True
                )
            conn.close()

            #向中心节点发送数据
            client = socket.socket()
            client.connect(('127.0.0.1',9999))
            client.send(self.data)
            print("数据已发送至server")
            client.close()


def main():

    global conf
    conf = Conf_resolver('./agent.conf')
    global conf_info
    conf_info = conf.conf_info
    server = SocketServer.ThreadingTCPServer((conf_info['agent_host'], conf_info['agent_port']), MyTCPHandler)
    server.serve_forever()
    

if __name__ == "__main__":
    main()

