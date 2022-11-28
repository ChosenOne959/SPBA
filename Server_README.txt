服务器端操作说明：
1. 打开服务器端服务程序：
1）按ctrl+R，输入cmd进入DOS
2）DOS中输入如下命令：
D:
cd SPBA/RPC
python RPC_server.py
（不要关闭该DOS窗口）
2. 打开Unreal相关项目并运行即可（位于D:/Unreal Projects目录下）

客户端说明：
使用前记得将客户端相关代码中所有建立的Multirotor & AirSimSettings对象赋予参数(is_localhost=False)
(不要将这部分修改传到git上，后面在新用户界面上写了客户端配置部分后就用用户界面操作了）

注：
若出现问题，用记事本打开D:/SPBA/RPC/RPC_server.py，将文件最后一行设置为start_server(is_localhost=False)
