#/usr/bin/python
#coding:utf8
import sys
import redis
import threading
from Queue import Queue

def conn(addr,output):
        try:
                w = open(output,'a')
                conn = redis.StrictRedis(addr,6379,socket_timeout=3)
                #dbname =  conn.config_get('databases')
                dbname =  conn.info('keyspace')
                for i in dbname:
                    db = "IP: " +addr  + " DBs: " + i
                    w.write(db)
                    print "IP: " + addr  + "\033[1;32;40m Redis Login Successful \033[0m"  + "DB: " + i
                conn.close()
                w.close()
        except:
               print "IP: " + addr  + "\033[1;31;40m Redis Login Failed \033[0m"

class MultiThread(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)
        def run(self):
                global queue
                while not queue.empty():
                        ip = queue.get()
                        conn(ip,sys.argv[1]+".txt")

if __name__ == "__main__":
        queue = Queue()
        a = open(sys.argv[1],'r')
        for ip in a.readlines():
                ip = ip.strip('\n')
                queue.put(ip)
        for i in range(1,99):
                c = MultiThread()
                c.start()
