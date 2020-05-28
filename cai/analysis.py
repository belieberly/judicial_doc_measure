import json
import re
from xml.etree import ElementTree as etree
import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sns
from utils.SVC.comment_predict import svm_predict_cai


def analysis_len(num):
    dic = {'案件基本情况': []}
    outfile = open('./data/len.json', 'w', encoding='utf-8')
    len_res = []
    count = 0
    path_file = open('G:/judicial_data/民事一审案件.tar/民事一审案件/path_min_pan_filter_len.txt', 'r', encoding='utf-8')
    for line in path_file.readlines():
        count += 1
        if count > num:
            break
        path = 'G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/' + line.strip()
        xml_file = etree.parse(path)
        root_node = xml_file.getroot()[0]
        for node in root_node:
            if node.tag == 'AJJBQK':
                AJJBQK_txt = node.get('value')
        pattern = r'，|。|；|：'
        sentence_list1 = re.split(pattern, AJJBQK_txt)
        for i in sentence_list1:
            if len(i) != 0:
                len_res.append(len(i))
    dic['案件基本情况'] = len_res
    json.dump(dic, outfile, ensure_ascii=False)
    return len_res


def confidenceinterval(data):  # 求置信区间
    StandardDeviation_sum = 0
    # 返回样本数量
    Sizeofdata = len(data)
    data = np.array(data)
    print(data)
    Sumdata = sum(data)
    # 计算平均值
    Meanvalue = Sumdata / Sizeofdata
    # print(Meanvalue)
    # 计算标准差
    for index in data:
        StandardDeviation_sum = StandardDeviation_sum + (index - Meanvalue) ** 2
    StandardDeviation_sum = StandardDeviation_sum / Sizeofdata
    StandardDeviationOfData = StandardDeviation_sum ** 0.5
    # print(StandardDeviationOfData)
    # 计算置信区间
    LowerLimitingValue = Meanvalue - 1 * StandardDeviationOfData
    UpperLimitingValue = Meanvalue + 1 * StandardDeviationOfData
    print('置信区间---------------')
    print(LowerLimitingValue)
    print(UpperLimitingValue)
    print('置信区间---------------')


def plot_show_volin(json_path, Chinese_name, English_name):
    file = open(json_path, 'r', encoding='utf-8')
    dic = json.load(file)
    len_ = dic[Chinese_name]
    confidenceinterval(len_)
    # volin图
    dataset = len_
    dataset.sort()
    dataset_ = dataset[0:int(0.90 * len(dataset))]
    print(len(dataset))

    confidenceinterval(dataset)
    sns.violinplot(data=dataset)
    plt.xlabel('Judicial Docs', fontsize=12)
    plt.ylabel(English_name, fontsize=12)
    plt.title("Volin Charts of " + English_name, fontsize=15)
    plt.savefig('./' + Chinese_name + '1.png')
    plt.show()
    confidenceinterval(dataset_)
    sns.violinplot(data=dataset_)
    plt.xlabel('Judicial Docs', fontsize=12)
    plt.ylabel(English_name, fontsize=12)
    plt.title("Volin Charts of " + English_name, fontsize=15)
    plt.savefig('./' + Chinese_name + '2.png')
    plt.show()
    sns.kdeplot(dataset_, shade=True, color="orange")
    plt.title('Density Plot of ' + English_name, fontsize=15)
    plt.legend()
    plt.savefig('./' + Chinese_name + '3.png')
    plt.show()
    return len_


def text_style_experiment(num, strip):
    dic = {}
    outfile = open('./data/text_style_' + str(strip) + '.json', 'w', encoding='utf-8')
    count = 0
    path_file = open('G:/judicial_data/民事一审案件.tar/民事一审案件/path_min_pan_filter_len.txt', 'r', encoding='utf-8')
    for line in path_file.readlines():
        count += 1
        if count > num:
            break
        path = 'G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/' + line.strip()
        print(path+' is processing')
        xml_file = etree.parse(path)
        root_node = xml_file.getroot()[0]
        for node in root_node:
            if node.tag == 'AJJBQK':
                AJJBQK_txt = node.get('value')
        sentiment_res, count = svm_predict_cai(AJJBQK_txt, strip)
        dic[line.strip()] = sentiment_res
    json.dump(dic, outfile, ensure_ascii=False)


if __name__ == '__main__':
    # res_len = analysis_len(10000)
    # print(res_len)
    # plot_show_volin('./data/len.json', '案件基本情况', 'AJJBQK')

    for i in range(8, 19):
        text_style_experiment(1000, i)
    # 长度区间为5-19
