#!/bin/sh

# 创建并设置VNC密码
mkdir -p ~/.vnc
echo $VNC_PASSWD | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# vnc 启动
vncserver $DISPLAY -geometry 2560x1600 -depth 24 # 执行 vncserver xxx 会自动执行 ~/.vnc/xstartup

# vnc 关闭
# vncserver -kill :1

# 启动 noVNC
cd /app/noVNC && ./utils/novnc_proxy --vnc localhost:$VNC_PORT --listen 0.0.0.0:6081

# 确保 非守护进程 无限挂起​
# tail -f /dev/null