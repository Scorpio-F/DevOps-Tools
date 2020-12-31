import os
import multiprocessing
path = '/H3C_Backup'
pool = multiprocessing.Pool()

def func(path):
    contents = os.walk(path, topdown=True)
    dir = []
    file = []
    for (root, dirs, files) in contents:
        dir.append(root)
        for i in files:
            file.append(root+'/'+i)
    return [dir, file]

content = func(path)

with open(path+'/'+'content.txt', 'w', encoding='utf-8') as f:
    for i in content[0]:
        f.write(i)
        f.write('\n')

with open(path+'/'+'file.txt', 'w', encoding='utf-8') as f:
    for i in content[1]:
        f.write(i)
        f.write('\n')