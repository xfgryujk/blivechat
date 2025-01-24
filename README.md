# blivechat

用于OBS的仿YouTube风格的bilibili直播评论栏

![OBS截图](./screenshots/obs.png)

![Chrome截图](./screenshots/chrome.png)

![样式生成器截图](./screenshots/stylegen.png)

## 特性

* 兼容YouTube直播评论栏的样式
* 高亮舰队、房管、主播的用户名
* 自带两种样式生成器，经典YouTube风格和仿微信风格
* 支持屏蔽弹幕、合并礼物等设置
* 支持前端直连B站服务器或者通过后端转发
* 支持自动翻译弹幕、醒目留言到日语，可以在后台配置翻译目标语言
* 支持标注打赏用户名的读音，可选拼音或日文假名
* 支持配置自定义表情，不需要开通B站官方表情
* 支持插件开发

## 使用方法

以下几种方式任选一种即可。**正式使用之前记得看[注意事项](https://github.com/xfgryujk/blivechat/wiki/%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A1%B9%E5%92%8C%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)**

推荐的方式：如果你需要使用插件、翻译等高级特性，则在本地使用；否则推荐直接通过公共服务器在线使用。因为本地使用时不会自动升级版本，有时候出了问题不能及时解决；但在线使用时会禁用部分高级特性，如果你有需要，只能本地使用了

### 一、在线使用

1. 这些是作者维护的公共服务器，根据情况随便选一个，直接用浏览器打开

    * [blive.chat](https://blive.chat/)：自动节点，一般等于cn.blive.chat，如果不可用了会进行切换，但切换需要一段时间
    * [cn.blive.chat](https://cn.blive.chat/)：墙内专用节点，不容易被墙，但如果受到攻击会变得不可用
    * [cloudflare.blive.chat](https://cloudflare.blive.chat/)：Cloudflare美国节点，不容易被攻击，但容易被墙
    * [vercel.blive.chat](https://vercel.blive.chat/)：Vercel美国节点，不容易被攻击，但容易被墙
    * [huggingface]
(https://asfag654-b.hf.space)：报脸服务器，中国大部分能裸连，但听说移动网可能连不上
 #### 报脸快速部署
  [点这里](https://huggingface.co/spaces/asfag654/b?duplicate=true&visibility=public)
  没有自己的数据库就~~乱填~~留空
2. 输入主播在开始直播时获得的身份码，复制房间URL
3. 用样式生成器生成样式，复制CSS
4. 在OBS中添加浏览器源，输入URL和自定义CSS

### 二、本地使用

1. 下载[本地分发版](https://github.com/xfgryujk/blivechat/releases)（仅提供x64 Windows版）。也可以在[B站商店](https://play-live.bilibili.com/details/1694397161340)下载
2. 双击`blivechat.exe`（或者`start.exe`）运行服务器
3. 用浏览器打开[http://localhost:12450](http://localhost:12450)，剩下的步骤和在线使用时是一样的

### 三、从源码运行

此方式适用于自建服务器或者在Windows以外的平台运行

0. 由于使用了git子模块，clone时需要加上`--recursive`参数：

    ```sh
    git clone --recursive https://github.com/xfgryujk/blivechat.git
    ```

    如果已经clone，拉子模块的方法：

    ```sh
    git submodule update --init --recursive
    ```

1. 编译前端（需要安装Node.js）：

    ```sh
    cd frontend
    npm i
    npm run build
    ```

2. 安装服务器依赖（需要Python 3.12以上版本）：

    ```sh
    pip install -r requirements.txt
    ```

3. 运行服务器：

    ```sh
    python main.py
    ```

    或者可以指定host和端口号：

    ```sh
    python main.py --host 127.0.0.1 --port 12450
    ```

4. 用浏览器打开[http://localhost:12450](http://localhost:12450)，以下略

### 四、Docker

此方式适用于自建服务器。示例的运行参数只是最基本的，可以根据需要修改

1.  ```sh
    docker run --name blivechat -d -p 12450:12450 \
      --mount source=blivechat-data,target=/mnt/data \
      xfgryujk/blivechat:latest
    ```

2. 用浏览器打开[http://localhost:12450](http://localhost:12450)，以下略

## 服务器配置

服务器配置文件在`data/config.ini`，可以配置数据库和允许自动翻译等，编辑后要重启生效

**自建服务器时强烈建议不使用加载器**，否则可能因为各种原因加载不出来

## 常用链接

* [文档](https://github.com/xfgryujk/blivechat/wiki)
* [交流社区](https://github.com/xfgryujk/blivechat/discussions)
* [B站商店](https://play-live.bilibili.com/details/1694397161340)
