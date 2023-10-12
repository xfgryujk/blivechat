这个目录用来暴露一些自定义文件给前端，例如图片、CSS、字体等
你可以在网页路径 “/custom_public/README.txt” 访问到这个文件
警告：不要在这个目录里存放密钥等敏感信息，因为可能会被远程访问

这个目录表下的 “preset.css” 文件是服务器预设CSS文件，你可以手动创建它
前端可以通过“导入服务器预设CSS”选项自动导入这个CSS，而不需要在OBS里面设置自定义CSS


This directory is used to expose some custom files to the front end, such as images, CSS, fonts, etc.
You can access this file on the web path: "/custom_public/README.txt"
WARNING: DO NOT store sensitive information such as secrets in this directory, because it may be accessed by remote

The "preset.css" file in this directory is the server preset CSS file. You can create it manually
The front end can automatically import this CSS through the "Import the server preset CSS" option, instead of
setting the custom CSS in OBS
