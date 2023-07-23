#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    @Author:V7hinc
    @Datetime:2021/11/15 15:23
    @Software:PyCharm
    @Filename:m3u8Downloader.py
"""

# 正式代码
import requests
import urllib.parse
import os
import time
import sys
import queue
import threading
import random
import string
from module.setting import ffmpeg


threadListSize = 48
queueSize = 96

_exitFlag = 0
_ts_total = 0
_count = 0
_dir = ''
_videoName = ''
_queueLock = threading.Lock()
_workQueue = queue.Queue(queueSize)
_threadList = []
for i in range(threadListSize):
    _threadList.append("Thread-" + str(i))


# threadList = ["Thread-1", "Thread-2", "Thread-3"]

class downloadThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        # print ("开启线程：" + self.name + '\n', end='')
        download_data(self.q)
        # print ("退出线程：" + self.name + '\n', end='')

down_failed_list = []
# 下载数据
def download_data(q):
    while not _exitFlag:
        _queueLock.acquire()
        if not _workQueue.empty():
            data = q.get()
            _queueLock.release()
            # print ("%s 使用了 %s" % (threadName, data) + '\n', end='')
            url = data
            retry = 5
            while retry:
                try:
                    r = session.get(url, timeout=20)
                    if r.ok:
                        file_name = url.split('/')[-1].split('?')[0]
                        # print(file_name)
                        with open(os.path.join(_dir, file_name), 'wb') as f:
                            f.write(r.content)
                        _queueLock.acquire()
                        global _count
                        _count = _count + 1
                        show_progress(_count / _ts_total)
                        _queueLock.release()
                        break
                except Exception as e:
                    print(e)
                    retry -= 1
            if retry == 0:
                print('[FAIL]%s' % url)
                down_failed_list.append(url)
        else:
            _queueLock.release()


# 填充队列
def fillQueue(nameList):
    _queueLock.acquire()
    for word in nameList:
        _workQueue.put(word)
        nameList.remove(word)
        if _workQueue.full():
            break
    _queueLock.release()


def get_session(pool_connections, pool_maxsize, max_retries):
    '''构造session'''
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize,
                                            max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# 展示进度条
def show_progress(percent):
    bar_length = 50
    hashes = '#' * int(percent * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [%s] %.2f%%" % (hashes + spaces, percent * 100))
    sys.stdout.flush()


def start(m3u8_url, dir, videoName):
    global _dir
    global _videoName
    global _ts_total
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    _dir = dir
    _videoName = videoName
    r = session.get(m3u8_url, timeout=10)
    if r.ok:
        body = r.content.decode()
        if body:
            ts_list = []
            body_list = body.split('\n')
            for n in body_list:
                if n and not n.startswith("#"):
                    ts_list.append(urllib.parse.urljoin(m3u8_url, n.strip()))
            if ts_list:
                _ts_total = len(ts_list)
                print('ts的总数量为：' + str(_ts_total) + '个')
                # 下载ts文件
                print('开始下载文件')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                res = download(ts_list)
                # res=True
                print('')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                if res:
                    # 整合ts文件
                    print('\n开始整合文件')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    ffmpeg_merge_file(ts_list, body_list)
                    print('')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                else:
                    print('下载失败')
    else:
        print(r.status_code)


def download(ts_list):
    threads = []
    threadID = 1
    # 创建新线程
    for tName in _threadList:
        thread = downloadThread(threadID, tName, _workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    ts_list_tem = ts_list.copy()
    fillQueue(ts_list_tem)
    # 等待队列清空
    while not _workQueue.empty():
        if _workQueue.full():
            pass
        else:
            fillQueue(ts_list_tem)
    # 通知线程是时候退出
    global _exitFlag
    _exitFlag = 1
    # 等待所有线程完成
    for t in threads:
        t.join()
    return True

def get_random(r_num):
    return ''.join(random.sample(string.digits * 2 + string.ascii_letters, r_num))


# 通过ffmpeg将TS文件整合在一起
def ffmpeg_merge_file(ts_list, body_list):
    index = 0
    global _dir
    ts_url_file_dict = {}
    while index < _ts_total:
        if ts_list[index] in down_failed_list:  # 当下载失败就不要了
            continue
        file_name = ts_list[index].split('/')[-1].split('?')[0]
        # print(file_name)
        percent = (index + 1) / _ts_total
        show_progress(percent)
        ts_file_path = os.path.join(_dir, file_name)
        ts_url_file_dict[ts_list[index]] = ts_file_path.replace('\\', '/')
        index += 1
    mod_m3u8_file = os.path.join(_dir, f'{get_random(20)}.m3u8')  # 存储ts本地路径的文件

    with open(mod_m3u8_file, 'w', newline='', encoding='utf-8') as f:
        for line in body_list:
            ts_url_file = ts_url_file_dict.get(line.strip())
            if ts_url_file is not None:  # 如果不为空说明是下载到本地了的ts文件
                write_content = ts_url_file
            else:
                write_content = line
            f.write(write_content+"\n")  # 把注释文件写在上面，有些是加密文件

    outfile = os.path.join(_dir, _videoName+'.mp4')
    # ffmpeg执行合并
    merge_cmd = f'{ffmpeg} -allowed_extensions ALL -protocol_whitelist "file,http,https,tls,crypto,tcp" -i {mod_m3u8_file} -c copy "{outfile}"'
    print(merge_cmd)
    os.popen(merge_cmd).read()

    # 清理ts数据
    os.remove(mod_m3u8_file)
    for ts_file in ts_url_file_dict.values():
        os.remove(ts_file)


def get_real_url(m3u8_url):
    r = session.get(m3u8_url, timeout=10)
    if r.ok:
        body = r.content.decode()
        if body:
            ts_url = ''
            body_list = body.split('\n')
            for n in body_list:
                if n and not n.startswith("#"):
                    ts_url = urllib.parse.urljoin(m3u8_url, n.strip())
            if ts_url != '':
                print('真实地址为' + ts_url)
                return ts_url
    else:
        print(r.status_code)


session = get_session(50, 50, 3)


def m3u8Downloader(m3u8_url_list: list, videoNameList: list, dirpath, ):
    # m3u8_url_list=[
    #     'https://v3.cdtlas.com/20210914/HWBb5ilr/index.m3u8'
    # ]
    for i in range(len(m3u8_url_list)):
        index = str(i + 1)
        url = m3u8_url_list[i]
        videoName = videoNameList[i]
        print(f"开始下载第{index}个视频:{videoName} url:{url}")
        # 是否需要获取真实的url
        # real_url = get_real_url(url)
        real_url = url
        global _exitFlag
        global _count
        _count = 0
        _exitFlag = 0
        start(real_url, dirpath, videoName)

