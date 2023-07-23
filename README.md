# m3u8_download
1、再通过m3u8Downloader ffmpeg下载ts合并
2、目前仅对centos7做了适配，其他有兴趣可以自行修改。大同小异


## 使用命令
> python运行,需要配置google浏览器驱动环境
```shell script
python3 m3u8_download.py -u "https://m3u.haiwaikan.com/xm3u8/3ed5cf6e7cbe2a1dd3137cc9c0d9eb1ac1cc92f317c3e029b236e7a30f314f009921f11e97d0da21.m3u8" -o "xiaoshideta"
```

> 自行构建docker
```shell script
docker build -t m3u8_download .
docker run --rm  -v `pwd`/log:/app/m3u8_download/src/log -it m3u8_download "-u https://m3u.haiwaikan.com/xm3u8/3ed5cf6e7cbe2a1dd3137cc9c0d9eb1ac1cc92f317c3e029b236e7a30f314f009921f11e97d0da21.m3u8 -o xiaoshideta"
```

> docker镜像直接拉取（推荐）
```shell script
docker pull ghcr.io/v7hinc/m3u8_download:latest
docker run --rm  -v `pwd`/log:/app/m3u8_download/src/log -it ghcr.io/v7hinc/m3u8_download:latest "-u https://m3u.haiwaikan.com/xm3u8/3ed5cf6e7cbe2a1dd3137cc9c0d9eb1ac1cc92f317c3e029b236e7a30f314f009921f11e97d0da21.m3u8 -o xiaoshideta"
```

## 报错解决
如果centos7使用docker运行时遇到挂载的目录提示Permission denied
可以尝试以下办法：
```
1.在运行容器的时候，给容器加特权，及加上 --privileged=true 参数：
docker run --privileged=true --rm  -v `pwd`/log:/app/m3u8_download/src/log -it ghcr.io/v7hinc/m3u8_download:latest "-u https://m3u.haiwaikan.com/xm3u8/3ed5cf6e7cbe2a1dd3137cc9c0d9eb1ac1cc92f317c3e029b236e7a30f314f009921f11e97d0da21.m3u8 -o xiaoshideta"
2.临时关闭selinux：
setenforce 0
```