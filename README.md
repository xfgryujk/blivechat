# blivechat
用于OBS的仿YouTube风格的bilibili直播聊天层

最近喜欢看VTuber，想为此写些程序，于是有了这个东西。~~写到一半发现有类似项目了：[bilibili-live-chat](https://github.com/Tsuk1ko/bilibili-live-chat)、[BiliChat](https://github.com/3Shain/BiliChat)。~~ 本项目就当做练手吧，而且对YouTube的模仿程度更高

![OBS截图](https://github.com/xfgryujk/blivechat/blob/master/screenshots/obs.png)  
![Chrome截图](https://github.com/xfgryujk/blivechat/blob/master/screenshots/chrome.png)  
![样式生成器截图](https://github.com/xfgryujk/blivechat/blob/master/screenshots/stylegen.png)  

## 特性
* 兼容YouTube直播chat的样式
* 金瓜子礼物模仿Super Chat显示
* 高亮舰队、房管、主播的用户名
* 支持屏蔽弹幕、限制最大速度等设置
* 自带样式生成器

## 使用方法
### 发布版
1. 下载[发布版](https://github.com/xfgryujk/blivechat/releases)（仅提供x64 Windows版）
2. 双击`blivechat.exe`运行服务器，或者用命令行可以指定host和端口号：
   ```bat
   blivechat.exe --host 127.0.0.1 --port 80
   ```
3. 用浏览器打开[http://localhost](http://localhost)，输入房间ID，进入房间，复制房间URL
4. （可选）用样式生成器生成样式，复制CSS
5. 在OBS中添加浏览器源，输入URL和自定义CSS，或者可以在首页的样式设置里输入CSS

### 源代码版
1. 编译前端（需要安装NPM）：
   ```sh
   cd frontend
   npm i
   npm run build
   ```
2. 运行服务器：
   ```sh
   python3 main.py
   ```
   或者可以指定host和端口号：
   ```sh
   python3 main.py --host 127.0.0.1 --port 80
   ```
3. 用浏览器打开[http://localhost](http://localhost)，输入房间ID，进入房间，复制房间URL
4. （可选）用样式生成器生成样式，复制CSS
5. 在OBS中添加浏览器源，输入URL和自定义CSS，或者可以在首页的样式设置里输入CSS

### 使用Docker运行(仅x64)
1. 安装[docker](https://www.runoob.com/docker/ubuntu-docker-install.html)
2. 安装镜像

   `docker build -t blivechat:latest .`

3. 运行镜像

   `docker run -d --name blivechat -p 80:80 blivechat`
   
   其中80:80的第一个80为映射到主机的端口号，可替换为其它端口。
3. 用浏览器打开[http://localhost](http://localhost)，输入房间ID，进入房间，复制房间URL
4. （可选）用样式生成器生成样式，复制CSS
5. 在OBS中添加浏览器源，输入URL和自定义CSS，或者可以在首页的样式设置里输入CSS
