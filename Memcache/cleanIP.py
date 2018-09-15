# encoding=utf-8
import telnetlib
import time
import sys
import os
import re
import Queue
import pprint
import threading


def main_thread(argv=None):
    if not argv:
        argv = sys.argv
    file_path = argv[1]
    output_file = argv[2]
    if os.path.exists(output_file):
        os.remove(output_file)

    count_total = 0
    ip_queue = Queue.Queue()
    # put ip address into Queue
    host_file = open(file_path, 'r')
    lines = host_file.readlines()
    for line in lines:
        if line.find("Discovered open port 11211/tcp on ") == -1:
            continue
        count_total += 1
        host = line[line.find("Discovered open port 11211/tcp on "):].strip()
        ip_queue.put(host)
    print ("Count_total = %d, ip_queue_size = %d" % (count_total, ip_queue.qsize()))
    host_file.close()

    host_file = open(output_file, 'a+')
    while not ip_queue.empty():
        host_file.writelines(ip_queue.get())
        host_file.writelines("\n")
    host_file.close()



if __name__ == '__main__':
    main_thread()
