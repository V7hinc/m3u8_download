FROM centos:7

COPY rely /app/m3u8_download/rely

WORKDIR /app/m3u8_download/rely

# 安装必要组件
RUN set -x;\
yum install unzip lrzsz python3 -y;\
tar -xvf ffmpeg-git-amd64-static.tar.xz -C /usr/local/;\
rm -rf ffmpeg-git-amd64-static.tar.xz;\
ln -s /usr/local/ffmpeg-git-20211108-amd64-static/ffmpeg /usr/bin/ffmpeg;

# 安装python脚本运行依赖模块组件
RUN set -x;\
pip3 install -r /app/m3u8_download/rely/requestsment.txt;

COPY src /app/m3u8_download/src
WORKDIR /app/m3u8_download/src

# 解决运行时编码问题
RUN set -x;\
echo 'export LC_ALL="en_US.utf8"' >> /etc/profile;\
echo 'export LANG="en_US.utf8"' >> /etc/profile;\
source /etc/profile

# 编写自启动脚本
RUN set -x;\
echo '#!/bin/sh' >> /auto_start.sh;\
echo 'source /etc/profile' >> /auto_start.sh;\
echo 'cd /app/m3u8_download/src' >> /auto_start.sh;\
echo 'python3 m3u8_download.py $1 $2' >> /auto_start.sh;\
chmod +x /auto_start.sh;

ENTRYPOINT ["/auto_start.sh"]
CMD ["-h"]




