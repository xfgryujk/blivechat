FROM ubuntu:bionic

COPY . ./blivechat

RUN apt update && apt install python3 wget git curl tar python3-distutils -y

RUN wget -q https://nodejs.org/dist/v10.16.0/node-v10.16.0-linux-x64.tar.xz && \
tar xf node-v10.16.0-linux-x64.tar.xz && \
ln -s /node-v10.16.0-linux-x64/bin/node /usr/bin/node && \
ln -s /node-v10.16.0-linux-x64/bin/npm /usr/bin/npm

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

RUN cd /blivechat/ && \ 
pip install -r requirements.txt && \
git reset --hard 2d86449 && \
git clone https://github.com/xfgryujk/blivedm.git && \
cd blivedm && git reset --hard 003d89e


RUN cd /blivechat/frontend && npm i && npm run build

CMD /usr/bin/python3 /blivechat/main.py --host 0.0.0.0 --port 80 
EXPOSE 80/tcp
EXPOSE 80/udp
