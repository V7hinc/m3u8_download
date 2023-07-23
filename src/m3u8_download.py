#!/usr/bin/env python3
#-*- coding:utf-8 -*-
"""
    @Author:V7hinc
    @Datetime:2021/11/15 10:52
    @Software:PyCharm
    @Filename:1.py
"""

# 正式代码
import os
from module.setting import BASE_DIR
from module.m3u8Downloader import m3u8Downloader


def get_args():
    import argparse

    parser = argparse.ArgumentParser()
    # 设置参数组required
    req_grp = parser.add_argument_group('required')
    req_grp.add_argument('-u', action="store", required=True, dest='m3u8_url', nargs=1, type=str, help='''使用360极速浏览器安装“猫抓”插件，访问https://www.haitu.tv搜索你想要的视频，在猫抓插件可以看到第一个m3u8结尾的url，例如：https://m3u.haiwaikan.com/xm3u8/3ed5cf6e7cbe2a1dd3137cc9c0d9eb1ac1cc92f317c3e029b236e7a30f314f009921f11e97d0da21.m3u8''')
    req_grp.add_argument('-o', action="store", required=True, dest='video_name', nargs=1, type=str, help="保存的视频名称")
    # 默认是可选组
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    video_url = args.m3u8_url[0]
    video_name = args.video_name[0]
    # 开始扫描视频
    m3u8_url_list = []
    m3u8_url_list.append(video_url)
    videoNameList = []
    videoNameList.append(video_name)
    if len(m3u8_url_list) > 0:
        m3u8Downloader(m3u8_url_list, videoNameList, os.path.join(BASE_DIR, 'log'))