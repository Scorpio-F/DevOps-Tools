import os
import time
import shutil
import multiprocessing
import requests


def init() :
    url = ['http://172.172.172.1:8000/file.txt', 'http://172.172.172.1:8000/content.txt']
    download_file = requests.get(url[0], stream=True)
    with open('/download/file.txt', 'wb') as f :
        for chunk in download_file.iter_content(chunk_size=4096) :
            f.write(chunk)

    download_content = requests.get(url[1], stream=True)
    with open('/download/content.txt', 'wb') as f :
        for chunk in download_content.iter_content(chunk_size=4096) :
            f.write(chunk)


def function(path) :
    # 通过os.walk()方法遍历到所有文件夹和文件
    file = []
    dir = []
    x = os.walk(path, topdown=True)
    for (root, dirs, files) in x :
        dir.append(root)
        for i in files :
            file.append(root + '/' + i)
    return [dir, file]


def check_dir(path) :
    # 获取本地目录
    x = function(path)
    dir_so = x[0]

    # 清洗服务端目录
    dirs = open('/download/content.txt', 'r', encoding='utf-8')
    dir_dst = dirs.readlines()
    dir_dst_info = []
    for i in dir_dst :
        i = i.replace('\n', '')
        print(i)
        dir_dst_info.append(i)

        # 比较目录，目录不一致就添加
    for i in dir_dst_info[1 :] + dir_so :
        if i not in dir_so :
            os.mkdir(i)
            print('创建了' + i)
        if i not in dir_dst_info :
            try :
                shutil.rmtree(i)
                print('删除了' + i)
            except :
                pass


def download(url, path) :
    download_file = requests.get(url, stream=True)
    with open(path, 'wb') as f :
        for chunk in download_file.iter_content(chunk_size=10240) :
            f.write(chunk)
            print('添加了' + path)


def check_file(path) :
    x = function(path)
    file_so = x[1]
    pool = multiprocessing.Pool(processes=10)
    # 清洗服务端文件
    files = open('/download/file.txt', 'r', encoding='utf-8')
    files_dst = files.readlines()
    files_dst_info = []
    for i in files_dst :
        i = i.replace('\n', '')
        files_dst_info.append(i)

    # 没有的下载,多余的删掉
    for i in file_so + files_dst_info :
        if i not in file_so :
            url = 'http://192.168.1.13:8000' + i
            pool.apply_async(download, (url, i,))

        if i not in files_dst_info :
            os.remove(i)
            print('删除了' + i)
    pool.close()
    pool.join()

if __name__ == '__main__' :
    path = '/H3C_Backup'
    init()
    check_dir(path)
    check_file(path)
