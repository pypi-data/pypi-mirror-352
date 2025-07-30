FROM ubuntu:24.04

# 将 docker 默认 shell 由 sh 改为 bash
SHELL ["/bin/bash", "-c"]

# 查看构建使用的用户 root
RUN whoami

RUN apt-get update && apt install -y \
  # 包含编译 C/C++ 程序所需的基础工具
  build-essential \
  # 提供 Linux 输入设备（如键盘、鼠标、触摸板等）的抽象层开发库
  libevdev-dev \
  # 安装与当前运行的内核版本匹配的内核头文件和开发包。
  linux-headers-generic

RUN apt-get update && apt-get install -y \
  # 一个非交互式的命令行下载工具，支持 HTTP、HTTPS 和 FTP 协议，常用于批量下载文件
  wget \
  # 类似 wget 的命令行工具，但更灵活，支持多种协议（HTTP/HTTPS/FTP/SCP 等），常用于 API 调用或脚本中下载资源
  curl \
  # 强大的命令行文本编辑器
  vim \
  git \
  # pyautogui.screenshot 低层会用到
  gnome-screenshot \
  # pyperclip 需要额外的工具如 xclip 或 xsel 来访问系统的剪贴板
  xclip \
  # 这是 Xfce 桌面环境的核心组件包，包含基本的功能和模块
  xfce4 \
  # 这是一个扩展包，提供额外的插件、工具和美化主题，增强 Xfce 的功能和用户体验
  xfce4-goodies \
  # 是一个开源的 ​​VNC（Virtual Network Computing）服务器软件​​，用于远程控制 Linux/Unix 系统的图形界面
  tightvncserver \
  # process "dbus-launch" (No such file ordirectory)
  # D-Bus 的 X11 扩展，用于进程间通信（IPC），支持图形界面和桌面环境的消息传递（如通知、剪贴板共享）
  dbus-x11 \
  # 用于支持中文显示
  ttf-wqy-zenhei \
  # 用于配置系统语言和区域设置（如日期格式、字符编码），安装后需运行 locale-gen 生成具体语言环境
  locales
  
# RUN apt-get update && apt-get install -y python3 python3-pip

# 设置系统语言为中文
RUN echo "zh_CN.UTF-8 UTF-8" >> /etc/locale.gen && \
  locale-gen && \
  update-locale LANG=zh_CN.UTF-8
ENV LANG zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

# npm 私有源
ENV NPM_REGISTRY_URL https://bnpm.byted.org/
# 设置 npm 私有源（nrm 不会修改 yarn 的源 手动修改）
ENV SET_NPM_REGISTRY_URL_CMD "npm config set registry $NPM_REGISTRY_URL && yarn config set registry $NPM_REGISTRY_URL && pnpm config set registry $NPM_REGISTRY_URL"

# 安装 nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# nvm install 镜像
ENV NVM_NODEJS_ORG_MIRROR https://npmmirror.com/mirrors/node
# 确保 nvm
ENV SET_NVM_CMD 'export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"; [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"'
RUN eval $SET_NVM_CMD \
  && echo "nvm version $(nvm -v)" \
  && nvm install v18.18.2 && npm i yarn pnpm pm2 -g --registry "$NPM_REGISTRY_URL" && eval $SET_NPM_REGISTRY_URL_CMD \
  && nvm alias default v18.18.2

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# uv python install 镜像
# ENV UV_PYTHON_INSTALL_MIRROR https://mirror.nju.edu.cn/github-release/indygreg/python-build-standalone/
# uv add 私有源
ENV UV_DEFAULT_INDEX https://bytedpypi.byted.org/simple
ENV PATH $PATH:$HOME/.local/bin
# 确保 uv
RUN source $HOME/.local/bin/env \
  && uv -V \
  && uv python install 3.11

WORKDIR /app

# TODO test mcp
COPY ./*.tar.gz /app/
RUN mkdir -p /app/pyautogui-extend \
  && eval $SET_NVM_CMD \
  && source $HOME/.local/bin/env \
  && cd /app \
  && tar -zxvf $(ls -t /app/*.tar.gz | head -n 1) -C /app/pyautogui-extend \
  && rm -rf $(ls -t /app/*.tar.gz | head -n 1) \
  && cd /app/pyautogui-extend \
  && pnpm i

# 安装 Cherry-Studio
# [安装 FUSE 参考](https://github.com/AppImage/AppImageKit/wiki/FUSE)
COPY ./Cherry-Studio-1.3.12-x86_64.AppImage /app/Cherry-Studio-1.3.12-x86_64.AppImage
RUN chmod +x /app/Cherry-Studio-1.3.12-x86_64.AppImage
# && apt-get update \
# # 它提供了管理 PPA（个人包档案）仓库的功能  确保 add-apt-repository 可用
# && apt-get install -y software-properties-common \
# libfuse2t64 \
# && add-apt-repository universe -y
# 命令行启动
# ./Cherry-Studio-1.3.12-x86_64.AppImage --appimage-extract-and-run --no-sandbox

# 安装飞书
COPY ./Feishu-linux_x64-7.36.11.deb /app/Feishu-linux_x64-7.36.11.deb
RUN dpkg -i /app/Feishu-linux_x64-7.36.11.deb \
  # 用于列出硬件信息的 Linux 工具。某些应用程序（比如飞书）可能会调用它来获取硬件信息，例如网卡、CPU、内存等
  # 飞书 需要
  # && apt-get install -y lshw \
  # 自动修复依赖
  && apt-get install -f
# 命令行启动
# bytedance-feishu-stable --no-sandbox

# 清理 不再需要的依赖包 缓存 以减小镜像体积
RUN apt-get -y autoremove \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# vnc 链接密码
ENV VNC_PASSWD 123456
# vncserver 启动需要这个环境变量
ENV USER $(whoami)
# pyautogui依赖于mouseinfo，而mouseinfo需要访问X Window System的显示服务器
# 用于指定图形界面显示设备的参数 对于 VNC 端口 :1 => 5901
ARG VNC_DISPLAY_NUM=1
ENV DISPLAY :${VNC_DISPLAY_NUM}
ENV VNC_PORT 590${VNC_DISPLAY_NUM}
# 暴露VNC端口
EXPOSE 5901
# 配置.xstartup文件以启动XFCE桌面环境
COPY xstartup /root/.vnc/xstartup

# novnc
RUN git clone https://github.com/novnc/noVNC.git
# 暴露novnc端口
EXPOSE 6081

COPY start.sh ./
CMD ["/app/start.sh"]
# docker run -itd --name ubuntu-nvm-uv -p 5901:5901 -p 6081:6081 ubuntu-nvm-uv:2025-05-30_16-16-46
