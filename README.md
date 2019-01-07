# FlaskWeb

# FlaskSite项目部署指南

- [x] **操作系统** Windows  **开发语言**  Python3.6 

## 1、为项目创建独立开发环境

通过virtualenv模块为FlaskSite项目创建一套独立的Python运行环境；然后通过requirements文件安装开发过程中涉及的第三方模块。具体步骤如下：

- 创建Python3虚拟环境 

```c
# 安装virtualenv模块
pip3 install virtualenv 
```

- 创建工作目录FlaskSite，将FlaskSite、Data文件夹复制到工作目录； 此步骤可通过手动直接操作，新建FlaskSite文件夹，复制粘贴FlasknSite、Data文件夹进入。
```c
# 命令行操作：
mkdir FlaskSite
cd FlaskSite
echo d|xcopy C:\Users\ShangFR\Desktop\FlaskSite FlaskSite /e
echo d|xcopy C:\Users\ShangFR\Desktop\Data Data /e
```

- 通过virtualenv模块创建一个独立的Python3运行环境，命名为PyEnv，激活虚拟环境，安装项目依赖；
```c
virtualenv PyEnv
# 激活虚拟环境
cd PyEnv\Scripts
activate
cd ..\..\FlaskSite
# 安装FlaskSite项目依赖库
pip3 install -r requirements.txt
```
## 2、运行FlaskSite

```
# 在虚拟环境下，进入FlaskSite文件夹，启动App.py
cd ..\..\FlaskSite
python App.py
# FlaskSite服务器已开启。 
```

## 3、查看FlaskSite      

打开浏览器，输入本地ip,端口号5000



