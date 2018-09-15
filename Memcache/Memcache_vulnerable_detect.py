# encoding=utf-8
import telnetlib
import time
import sys
import os
import re
import Queue
import pprint
import threading


class MemcachedStats:

    _client = None
    _key_regex = re.compile(r'ITEM (.*) \[(.*); (.*)\]')
    _slab_regex = re.compile(r'STAT items:(.*):number')
    _stat_regex = re.compile(r"STAT (.*) (.*)\r")

    def __init__(self, host='localhost', port='11211', timeout=3):
        self._host = host
        self._port = port
        self._timeout = timeout

    @property
    def client(self):
        if self._client is None:
            self._client = telnetlib.Telnet(self._host, self._port,
                                            self._timeout)
        return self._client

    def command(self, cmd):
        #  Write a command to telnet and return the response
        self.client.write(("%s\n" % cmd).encode('ascii'))
        try:
            return self.client.read_until(b'END', timeout=3)  # .decode('ascii')
        except:
            return "got exception"

    def key_details(self, sort=True, limit=100):
        # Return a list of tuples containing keys and details
        cmd = 'stats cachedump %s %s'
        keys = [key for id in self.slab_ids()
            for key in self._key_regex.findall(self.command(cmd % (id, limit)))]
        if sort:
            return sorted(keys)
        else:
            return keys

    def keys(self, sort=True, limit=100):
        # Return a list of keys in use
        try:
            return [key[0] for key in self.key_details(sort=sort, limit=limit)]
        except Exception, e:
            return str(e)

    def slab_ids(self):
        #  Return a list of slab ids in use
        return self._slab_regex.findall(self.command('stats items'))

    def stats(self):
        # Return a dict containing memcached stats
        try:
            return dict(self._stat_regex.findall(self.command('stats')))
        except Exception, e:
            return str(e)


def write_file(filename, content):
    host_file = open(filename, 'a+')
    for var in content:
        host_file.writelines(var)
    host_file.writelines("\n")
    host_file.close()


def worker(output_file, queue, lock):
    while True:
        host = queue.get()
        port = '11211'
        print time.asctime(), ":   ****** try", "", host, "", ""
        m = MemcachedStats(host, port)

        if lock.acquire(True):
            data = time.asctime() + ":   ****** try    " + host
            write_file(output_file, data)
            write_file(output_file, pprint.pformat(m.keys()))
            lock.release()
        queue.task_done()


def main(argv=None):
    if not argv:
        argv = sys.argv
    file_path = argv[1]
    output_file = argv[2]
    if os.path.exists(output_file):
        os.remove(output_file)

    index = 0
    count_total = 0
    list_data = []

    print time.asctime(), ":   ****** begin"
    list_data.append(time.asctime() + ":   ****** begin")
    write_file(output_file, list_data)
    del list_data[0]

    host_file = open(file_path, 'r')
    lines = host_file.readlines()
    for line in lines:
        if line.find("Discovered open port 11211/tcp on ") == -1:
            continue
        count_total += 1
    print count_total
    host_file.close()

    host_file = open(file_path, 'r')
    lines = host_file.readlines()
    for line in lines:
        if line.find("Discovered open port 11211/tcp on ") == -1:
            continue
        index += 1
        host = line[line.find("Discovered open port 11211/tcp on ") + 34:].strip()
        port = '11211'
        percent = float(index)/float(count_total) * 100
        print index, time.asctime(), ":   ****** try", "", host, "", "", percent, "%"
        list_data.append(str(index) + "    " + time.asctime() + ":   ****** try    " + host)
        write_file(output_file, list_data)
        del list_data[0]

        import pprint
        m = MemcachedStats(host, port)
        # pprint.pprint(m.keys())
        write_file(output_file, pprint.pformat(m.keys()))

    host_file.close()
    print time.asctime(), ":   ****** end!"
    list_data.append(time.asctime() + ":   ****** end!")
    write_file(output_file, list_data)
    del list_data[0]


def main_thread(argv=None):
    if not argv:
        argv = sys.argv
    file_path = argv[1]
    output_file = argv[2]
    if os.path.exists(output_file):
        os.remove(output_file)

    count_total = 0
    num_worker_threads = 5

    # put ip address into Queue
    host_file = open(file_path, 'r')
    lines = host_file.readlines()
    for line in lines:
        if line.find("Discovered open port 11211/tcp on ") == -1:
            continue
        count_total += 1
        host = line[line.find("Discovered open port 11211/tcp on ") + 34:].strip()
        ip_queue.put(host)
    print ("Count_total = %d, ip_queue_size = %d" % (count_total, ip_queue.qsize()))
    host_file.close()

    for i in range(num_worker_threads):
        t = threading.Thread(target=worker, args=(output_file, ip_queue, mu))
        t.daemon = True
        t.start()

    ip_queue.join()       # block until all tasks are done


ip_queue = Queue.Queue()  # global var for ip address
mu = threading.Lock()     # lock for file write

if __name__ == '__main__':
    main_thread()
