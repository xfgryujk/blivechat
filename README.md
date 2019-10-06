# blivechat
用于OBS的仿YouTube风格的bilibili直播评论栏

最近喜欢看VTuber，想为此写些程序，于是有了这个东西。~~写到一半发现有类似项目了：[bilibili-live-chat](https://github.com/Tsuk1ko/bilibili-live-chat)、[BiliChat](https://github.com/3Shain/BiliChat)。~~ 本项目就当做练手吧，而且对YouTube的模仿程度更高

![OBS截图](https://github.com/xfgryujk/blivechat/blob/master/screenshots/obs.png)  
![Chrome截图](https://github.com/xfgryujk/blivechat/blob/master/screenshots/chrome.png)  
![样式生成器截图](https://github.com/xfgryujk/blivechat/blob/master/screenshots/stylegen.png)  

## 特性
* 兼容YouTube直播评论栏的样式
* 金瓜子礼物模仿醒目留言显示
* 高亮舰队、房管、主播的用户名
* 支持屏蔽弹幕、限制最大速度等设置
* 自带样式生成器

## 使用方法
### 本地使用
1. 下载[发布版](https://github.com/xfgryujk/blivechat/releases)（仅提供x64 Windows版）
2. 双击`blivechat.exe`运行服务器，或者用命令行可以指定host和端口号：
   ```bat
   blivechat.exe --host 127.0.0.1 --port 12450
   ```
3. 用浏览器打开[http://localhost:12450](http://localhost:12450)，输入房间ID，保存配置，复制房间URL
4. 用样式生成器生成样式，复制CSS
5. 在OBS中添加浏览器源，输入URL和自定义CSS，或者可以在首页的样式设置里输入CSS

### 公共服务器
请优先在本地使用，使用公共服务器会有更大的弹幕延迟，而且服务器故障时可能出现直播事故

* [第三方公共服务器](http://chat.bilisc.com/)
* [仅样式生成器](https://style.vtbs.moe/)

### 源代码版
1. 编译前端（需要安装Node.js和npm）：
   ```sh
   cd frontend
   npm i
   npm run build
   ```
2. 运行服务器（需要Python3.6以上版本）：
   ```sh
   pip3 install -r requirements.txt
   python3 main.py
   ```
   或者可以指定host和端口号：
   ```sh
   python3 main.py --host 127.0.0.1 --port 12450
   ```
3. 用浏览器打开[http://localhost:12450](http://localhost:12450)，以下略

### Docker
1. ```sh
   docker run -d -p 12450:12450 xfgryujk/blivechat:latest
   ```
2. 用浏览器打开[http://localhost:12450](http://localhost:12450)，以下略
