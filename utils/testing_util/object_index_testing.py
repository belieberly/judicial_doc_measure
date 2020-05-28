

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


acc_GCSX_system = [6, 10, 8, 10, 10, 8, 8, 6, 10, 6, 10, 6, 8, 6, 8, 8]
acc_GCSX_person = [8, 10, 8, 8, 10, 8, 8, 8, 10, 8, 10, 8, 8, 8, 8, 8]
acc_GCSX_score = 10.0

acc_SFCD_system = [0, 1, 5, 5, 5, 1, 5, 0, 5, 0, 5, 0, 1, 0, 5, 5]
acc_SFCD_person = [5, 1, 5, 5, 5, 1, 5, 1, 5, 1, 5, 5, 1, 1, 5, 5]
acc_SFCD_score = 5.0

com_PJNR_system = [5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 3, 5, 5, 5, 5, 5]
com_PJNR_person = [3, 3, 5, 2, 5, 3, 3, 3, 5, 5, 3, 5, 3, 5, 5, 4]
com_PJNR_score = 5.0

con_pun_system = [2, 6, 8, 2, 7, 5, 7, 9, 7, 9, 10, 9, 1, 1, 9, 0]
con_pun_person = [2, 6, 9, 3, 7, 4, 7, 9, 7, 8, 10, 8, 2, 2, 8, 0]
con_pun_score = 10.0

acc_SLJG_system = [8, 8, 9, 6, 4, 6, 6, 8, 6, 6, 9, 6, 4, 4, 6, 7]
acc_SLJG_person = [8, 8, 10, 6, 4, 6, 6, 8, 6, 6, 10, 6, 6, 4, 6, 10]
acc_SLJL_score = 10.0

rea_ZYJD_system = [0, 0, 5, 5, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5]
rea_ZYJD_person = [0, 0, 5, 5, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 5, 5]
rea_ZYJD_score = 5.0



def fangcha(l):
    length = len(l)
    avg = sum(l)/length
    tmp = 0
    for i in range(length):
        tmp += (l[i]-avg)*(l[i]-avg)
    res = tmp/length
    return res
def diff(system, person, score):
    diff_list = []
    for i in range(len(system)):
        diff_list.append((system[i] - person[i]) / score)
    return diff_list
def diff_l(system,person):
    diff_list = []
    for i in range(len(system)):
        diff_list.append(system[i] - person[i])
    return diff_list

def compute(system,person):
    system_avg = sum(system)/len(system)
    person_avg = sum(person)/len(system)
    data = pd.DataFrame({'system':system,'person':person})
    diff_list = diff_l(system,person)
    max_diff = max(diff_list)
    min_diff = min(diff_list)
    diff_fangcha = fangcha(diff_list)
    print(system_avg,person_avg,diff_fangcha,max_diff,min_diff)
    #pearson系数，连续性变量
    print(data.corr())
    #kendall系数，定序变量
    print(data.corr('kendall'))
    #spearman系数，定序变量
    print(data.corr('spearman'))


print('acc_SLJG')
compute(acc_SLJG_system,acc_SLJG_person)
print('acc_GCSX')
compute(acc_GCSX_system,acc_GCSX_person)
print('com_PJNR')
compute(com_PJNR_system,com_PJNR_person)
print('con_pun')
compute(con_pun_system,con_pun_person)


print('统计')
a = acc_SLJG_system
a.extend(acc_GCSX_system)
a.extend(com_PJNR_system)
a.extend(con_pun_system)

b = acc_SLJG_person
b.extend(acc_GCSX_person)
b.extend(com_PJNR_person)
b.extend(con_pun_person)
compute(a,b)





def zhexian():
    # 这里导入你自己的数据

    x_axix = [i for i in range(16)]

    # 开始画图
    plt.title('Result Analysis')
    plt.plot(x_axix, diff(acc_GCSX_system, acc_GCSX_person, acc_GCSX_score), color='green', label='acc_GCSX')
    plt.plot(x_axix, diff(acc_SLJG_system, acc_SLJG_person, acc_SLJL_score), color='skyblue', label='acc_SLJG')
    # plt.plot(x_axix, diff(com_PJNR_system, com_PJNR_person, com_PJNR_score), color='red', label='com_PJNR')
    plt.plot(x_axix, diff(con_pun_system, con_pun_person, con_pun_score), color='red', label='con_pun')
    plt.legend()  # 显示图例
    plt.ylim(-1, 1)

    plt.xlabel('score_diff')
    plt.ylabel('judicial_doc')
    plt.show()
    # python 一个折线图绘制多个曲线
    plt.savefig('../../data/zhexian.png')

def diff_num(system, person):
    num = 0
    total = len(system)
    for i in range(len(system)):
        if system[i] == person[i]:
            num += 1
    return num, total


def bing(system, person):
    num, total = diff_num(system, person)
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['axes.unicode_minus'] = False

    label_list = ["same", "different"]  # 各部分标签
    size = [num / total * 100, (total - num) / total * 100]  # 各部分大小
    color = ["skyblue", "aliceblue"]  # 各部分颜色
    explode = [0.05, 0]  # 各部分突出值

    """
    绘制饼图
    explode：设置各部分突出
    label:设置各部分标签
    labeldistance:设置标签文本距圆心位置，1.1表示1.1倍半径
    autopct：设置圆里面文本
    shadow：设置是否有阴影
    startangle：起始角度，默认从0开始逆时针转
    pctdistance：设置圆内文本距圆心距离
    返回值
    l_text：圆内部文本，matplotlib.text.Text object
    p_text：圆外部文本
    """

    patches, l_text, p_text = plt.pie(size, explode=explode, colors=color, labels=label_list, labeldistance=1.1,
                                      autopct="%1.1f%%", shadow=False, startangle=90, pctdistance=0.6)
    plt.axis("equal")  # 设置横轴和纵轴大小相等，这样饼才是圆的
    plt.title("客观指标评估命中情况分析")
    plt.legend()
    plt.savefig('../../data/bing.eps')
    plt.show()



acc_SFCD_system.extend(rea_ZYJD_system)
acc_SFCD_person.extend(rea_ZYJD_person)
bing(acc_SFCD_system, acc_SFCD_person)
# zhexian()
