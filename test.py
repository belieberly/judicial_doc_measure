# import json
#
# file = open('web_data/writ_report/27d57c1f-e53f-4bda-ae21-621989ad3bd7.json','r',encoding = 'utf-8')
# print(json.load(file))

import threading
import time

import multiprocessing
# import time
# import random
#
#
# def func(msg):
#     print("in:", msg)
#     time.sleep(random.randint(3, 10))
#     print("out,", msg)
#     return msg,msg


# if __name__ == "__main__":
#     # 这里设置允许同时运行的的进程数量要考虑机器cpu的数量，进程的数量最好小于cpu的数量，
#     # 因为大于cpu的数量，增加了任务调度的时间，效率反而不能有效提高
#     pool = multiprocessing.Pool()
#     dic = []
#     item_list = ['processes1', 'processes2', 'processes3', 'processes4', 'processes5', ]
#     count = len(item_list)
#     for item in item_list:
#         msg = "python教程 %s" % item
#         # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
#         dic.append(pool.apply_async(func, [msg]))
#     pool.close()
#     pool.join()
#     for i in dic:
#         print(i.get())
 # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束

# import multiprocessing
# import time

# def func(msg):
#     print("msg:", msg)
#     time.sleep(3)
#     print("end")
#     return "done" + msg
#
# if __name__ == "__main__":
#     pool = multiprocessing.Pool(processes=4)
#     result = []
#     for i in range(3):
#         msg = "hello %d" %(i)
#         result.append(pool.apply_async(func, (msg, )))
#     pool.close()
#     pool.join()
#     for res in result:
#         print(":::", res.get())
#     print("Sub-process(es) done.")


file = open('G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/1001559.xml','r',encoding = 'utf-8')
test_out = open('./test_xml.xml','w',encoding = 'utf-8')
for line in file.readlines():
    test_out.write(line)
