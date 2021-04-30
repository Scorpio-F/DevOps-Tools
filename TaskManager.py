import paramiko
import os
import threading

"""
概述：
批量ssh，sftp刷命令或者传文件，支持多线程。

使用说明：
实例化Tasks类，并调用其中的ssh()方法刷命令，sftp_get/put()方法传文件。

传参说明：
Tasks类初始化必须要传入ip地址列表和命令列表。 注意！ 一个ip地址对应一个命令列表！
semaphore参数是信号量：多线程同时运行的最大线程数，默认为5。
source_file参数是源文件路径，必须是文件，不能是文件夹。
destination_file参数是目的文件路径，必须是文件，不能是文件夹。

其他说明：
执行完命令的结果默认存在/tmp/TaskManager/下
ssh默认读取/root/.ssh/id_rsa下的密钥， username默认为root， 端口号默认22

"""


class TaskManager:
    def __init__(self):
        """
        初始化
        """
        self.username = 'root'
        self.port = 22
        self.pkey = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')

    def sftp_client(self, ip):
        """
        sftp
        基于paramiko的sftp
        """
        client = paramiko.Transport(ip, self.port)
        client.connect(username=self.username, pkey=self.pkey)
        sftp = paramiko.SFTPClient.from_transport(client)
        return sftp

    def ssh_client(self, ip, command):
        """
        ssh
        基于paramiko的ssh
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, self.port, self.username, pkey=self.pkey)
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        result = stdout.read().decode('utf-8')
        if os.path.exists('/tmp/TaskManager/') is False:
            os.mkdir('/tmp/TaskManager/')
        with open('/tmp/TaskManager/%s_result.log' % ip, 'a') as f:
            f.write(result)
            f.write('\n')
        client.close()
        print(ip, '的命令刷完了')

    def put_file(self, ip, source_file, destination_file):
        """
        上传文件
        接收源文件路径和目的文件路径参数
        """
        if os.path.exists(source_file) is True:
            try:
                sftp = self.sftp_client(ip)
                sftp.put(source_file, destination_file)
                print(ip, '传完了')
            except Exception as e:
                return e
        else:
            return '该文件不存在,请传入一个正确的文件路径'

    def get_file(self, ip, source_file, destination_file):
        """
        下载
        同put
        """
        if os.path.exists(source_file) is True:
            try:
                sftp = self.sftp_client(ip)
                sftp.get(source_file, destination_file)
                print(ip, '下完了')
            except Exception as e:
                return e
        else:
            return '该文件不存在,请传入一个正确的文件路径'


class TasksThread(threading.Thread):
    """
    多线程
    封装信号量
    """
    def __init__(self,  args=(), group=None, target=None, name=None, kwargs=None, *, daemon=None, semaphore):
        super(TasksThread,self).__init__(target=target, args=args, kwargs=kwargs)
        self.args = args
        self.kwargs = kwargs
        self.target = target
        self.semaphore = threading.BoundedSemaphore(semaphore)

    def run(self):
        self.semaphore.acquire()
        self.target(*self.args)
        self.semaphore.release()


class Tasks(TaskManager):
    """
    封装上面两个类，便于调用
    """
    def __init__(self, ip, command):
        super(Tasks, self).__init__()
        self.ip = ip
        self.command = command

    def ssh(self, semaphore=5):
        lst = [TasksThread(target=TaskManager().ssh_client, args=(i, ';'.join(self.command),), semaphore=semaphore) for i in self.ip]
        for i in lst:
            i.start()

    def sftp_get(self, source_file, destination_file, semaphore=5):
        lst = [TasksThread(target=TaskManager().get_file, args=(i, source_file, destination_file,), semaphore=semaphore) for i in self.ip]
        for i in lst:
            i.start()

    def sftp_put(self, source_file, destination_file, semaphore=5):
        lst = [TasksThread(target=TaskManager().get_file, args=(i, source_file, destination_file,), semaphore=semaphore) for i in self.ip]
        for i in lst:
            i.start()


#  Example:
#     ip = ['192.168.0.117', '192.168.0.148']
#     x = Tasks(ip=ip, command=['df -h', 'ip a'])
#     x.ssh()
