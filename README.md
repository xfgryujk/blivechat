# blivechat
用于OBS的仿YouTube风格的bilibili直播聊天层

最近喜欢看VTuber，想为此写些程序，于是有了这个东西。~~写到一半发现有类似项目了，而且还是纯前端实现的：[bilibili-live-chat](https://github.com/Tsuk1ko/bilibili-live-chat)。~~ 本项目就当做练手吧，而且对YouTube的模仿程度更高（指样式和Super Chat）

![截图](https://github.com/xfgryujk/blivechat/blob/master/screenshot.png)  

## 特性
* 兼容YouTube直播chat的样式，生成样式参考[https://chatv2.septapus.com/](https://chatv2.septapus.com/)
* 金瓜子礼物模仿Super Chat显示
* 高亮舰队、房管、主播的用户名

## 使用方法
1. 编译前端（需要安装NPM）：
   ```sh
   cd frontend
   npm i
   npm build
   ```
2. 运行服务器：
   ```sh
   python3 main.py
   ```
3. 用浏览器打开[http://localhost](http://localhost)，输入房间号，进入，复制房间URL（其实就是http://localhost/room/<房间ID>）
4. （可选）在[https://chatv2.septapus.com/](https://chatv2.septapus.com/)生成样式，复制CSS
5. 在OBS中添加浏览器源，输入URL和自定义CSS
