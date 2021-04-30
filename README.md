# DevOps-Tools
七杂八杂的运维脚本

## 1、TaskManager V.1
#### 概述：
- 批量ssh，sftp刷命令或者传文件，支持多线程。

#### 使用说明：
- 实例化Tasks类，并调用其中的ssh()方法刷命令，sftp_get/put()方法传文件。


#### 传参说明：
- Tasks类初始化必须要传入ip地址列表和命令列表。 **注意！ 一个ip地址对应一个命令列表！**
- semaphore参数是信号量：多线程同时运行的最大线程数，默认为5。
- source_file参数是源文件路径，必须是文件，不能是文件夹。
- destination_file参数是目的文件路径，必须是文件，不能是文件夹。

#### 其他说明：
- 执行完命令的结果默认存在/tmp/TaskManager/下
- ssh默认读取/root/.ssh/id_rsa下的密钥， username默认为root， 端口号默认22

#### 例子：
新建一个.py
```python
import TaskManager

ip = ['192.168.0.117', '192.168.0.148']
x = Tasks(ip=ip, command=['df -h', 'ip a'])
x.ssh()
```
或者在本脚本下添加:
```python
if __name__ == '__main__':
  ip = ['192.168.0.117', '192.168.0.148']
  x = Tasks(ip=ip, command=['df -h', 'ip a'])
  x.ssh()
```
