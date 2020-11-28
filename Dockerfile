# 运行时
FROM python:3.6.8-slim-stretch
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch main contrib non-free">>/etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-updates main contrib non-free">>/etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-backports main contrib non-free">>/etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian-security stretch/updates main contrib non-free">>/etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y wget tar xz-utils
RUN wget https://nodejs.org/dist/v10.16.0/node-v10.16.0-linux-x64.tar.xz \
    && tar -xvf node-v10.16.0-linux-x64.tar.xz \
    && rm node-v10.16.0-linux-x64.tar.xz \
    && ln -s /node-v10.16.0-linux-x64/bin/node /usr/local/bin/node \
    && ln -s /node-v10.16.0-linux-x64/bin/npm /usr/local/bin/npm

# 后端依赖
WORKDIR /blivechat
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 前端依赖
WORKDIR ./frontend
COPY frontend/package.json ./
RUN npm i --registry=https://registry.npm.taobao.org

# 编译前端
COPY . ../
RUN npm run build

# 运行
WORKDIR ..
VOLUME /blivechat/data /blivechat/log /blivechat/frontend/dist
EXPOSE 12450
ENTRYPOINT ["python3", "main.py"]
CMD ["--host", "0.0.0.0", "--port", "12450"]
