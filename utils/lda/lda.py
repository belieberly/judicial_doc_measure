from xml.etree import ElementTree as etree
from gensim import corpora, models,similarities
import numpy as np
import pandas as pd
import re
import logging
import multiprocessing
from normalize import normalizer
import os
import json
import config as cf

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

SOME_FIXED_SEED = 20


replace_numbers = re.compile(r'\d+', re.IGNORECASE)
normalizer_ = normalizer('E:/pycharm/judicial_doc_measurement/utils/lda/word.txt')
word_len = 2
progress = 0


#获取单篇文章的法条
def get_law(node):
    law_tmp = ''
    law_list = []
    for subnode in node:
        if subnode.tag == 'FLFTFZ':
            name = ''
            for subsubnode in subnode:
                if subsubnode.tag == 'MC':
                    name = subsubnode.get('value')
                elif subsubnode.tag == 'T':
                    law_list.append(name + subsubnode.get('value'))
    # print(law_list)
    law_tmp = ';'.join(law_list)

    return (law_tmp)


# xml_file = etree.parse("D:/NJU/final_project/data/example/100032.xml")
# root_node = xml_file.getroot()[0]
# print(root_node)
# for node in root_node:
#     law_tmp=''
#     if node.tag == 'CPFXGC':
#         print('caipanfenxiguocheng')
#         for subnode in node:
#             if subnode.tag == 'FLFTYY':
#                 print('falvfatiaoyinyong')
#                 law_tmp = get_law(subnode)
#     print(law_tmp)

#
def data_preprocess():
    path_txt = open('G:/judicial_data/民事一审案件.tar/民事一审案件/path_min_pan_filter_len.txt', 'r', encoding='utf-8')
    count = 0
    alltext = []
    law = []
    anyou = []
    path = []
    for line in path_txt.readlines():
        xml_file = etree.parse('G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/' + line.strip())
        root_node = xml_file.getroot()[0]
        text_tmp = ''
        anyou_tmp = ''
        law_tmp = ''
        for node in root_node:
            if node.tag == 'AJJBQK':
                # print(node.get('value'))
                text_tmp = node.get('value')
            elif node.tag == 'SSJL':
                for subnode in node:
                    if subnode.tag == 'AY':
                        anyou_tmp = subnode.get('value')
            elif node.tag == 'CPFXGC':
                for subnode in node:
                    if subnode.tag == 'FLFTYY':
                        law_tmp = get_law(subnode)
                count += 1
        # print(text_tmp,anyou_tmp,law_tmp)
        if text_tmp!='' and anyou_tmp!='' and law_tmp!='':
            alltext.append(text_tmp)
            anyou.append(anyou_tmp)
            law.append(law_tmp)
            path.append(line.strip())
        # 设置数据量
        if count>=10000:
            break
        print(count)
    print(len(alltext))
    print('数据读取完成')
    return alltext,anyou,law,path

def raw_text_csv(alltext,anyou,law,path):
    df = pd.DataFrame({'text': alltext, 'anyou': anyou, 'law': law, 'path': path})
    df.to_csv('E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/raw_text.csv', encoding="utf-8-sig")
    print(len(df))
    print('raw_text.csv存储完成')

def text_to_wordlist(text):
    # print('------------text:'+text)
    return " ".join(normalizer_.seg_one_text(text,2))


def multi_preprocess(comments=[]):
    pool_size = 5 #multiprocessing.cpu_count() + 1
    print("pool_size", pool_size)
    pool = multiprocessing.Pool(pool_size)
    pool_outputs = pool.map(text_to_wordlist, comments)
    pool.close()
    pool.join()

    print('successful')

    return pool_outputs



def cut_text(alltext):
    comments = multi_preprocess(comments=alltext)
    return comments

def process_csv(alltext):
    train_data = cut_text(alltext)
    df = pd.DataFrame({'text': train_data})
    df.to_csv('E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/process.csv', encoding="utf-8-sig")
    print('process.csv存储成功')


def lda():
    data = pd.read_csv("./lda_model/process.csv", encoding="utf-8", header=None)
    # data[2] = data[1].apply(lambda x: re.split(r'\s*', x))
    data[2] = data[1].apply(lambda x: x.split(' '))

    corpora_documents = []
    # print(data[2])
    for item_str in data[2]:
        # print(item_str)
        corpora_documents.append(item_str)
    del corpora_documents[0]

    print(corpora_documents[0])

    dict_1 = corpora.Dictionary(corpora_documents)
    dict_1.save('./lda_model/dict_v2')
    dict_corpora = [dict_1.doc2bow(i) for i in corpora_documents]
    print('字典构建完成')

    # 向量的每一个元素代表了一个word在这篇文档中出现的次数
    # print(corpus)
    from gensim.corpora.mmcorpus import MmCorpus

    MmCorpus.serialize('ths_corpora.mm', dict_corpora)

    tfidf = models.TfidfModel(dict_corpora)
    corpus_tfidf = tfidf[dict_corpora]
    tfidf.save("./lda_model/my_model.tfidf")
    np.random.seed(SOME_FIXED_SEED)
    lda = models.LdaModel(corpus_tfidf, num_topics=78, id2word=dict_1, iterations=1000)
    # # #
    lda.save('./lda_model/mylda_v2')
    lda.show_topics()

def recommender(file_path):
    lda = models.LdaModel.load('E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/mylda_v2')
    dict_1 = corpora.Dictionary.load('E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/dict_v2')
    tfidf = models.TfidfModel.load("E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/my_model.tfidf")
    dict_corpora = corpora.mmcorpus.MmCorpus('E:/pycharm/judicial_doc_measurement/utils/lda/ths_corpora.mm')
    corpus_tfidf = tfidf[dict_corpora]
    law_tmp = []


    #样例输入
    xml_file = etree.parse(file_path)
    root_node = xml_file.getroot()[0]
    for node in root_node:
        if node.tag == 'AJJBQK':
            text = node.get('value')
        elif node.tag == 'CPFXGC':
            for subnode in node:
                if subnode.tag == 'FLFTYY':
                    law_tmp = get_law(subnode).split(';')
    processed_fact = text_to_wordlist(text)

    fact = processed_fact.split(' ')
    unseen_doc = dict_1.doc2bow(fact)
    vector = lda[unseen_doc]
    print('lda结果')
    print(vector)

    #按照第一列的负数排序
    topic = sorted(vector, key=lambda item: -item[1])[0:1]
    topic_num = []
    for i in topic:
        topic_num.append(i[0])
    print('topic_num')
    print(topic_num)
    keyword = []
    for q in topic_num:
        print("%d topic:%s" % (q, lda.print_topic(q)))

    with open("E:/pycharm/judicial_doc_measurement/utils/lda/lda-docs-data.json")as f:
        data = f.read()
    dict = json.loads(data)

    search_corpus = []
    index_num = 0
    index_dict = {}
    for q in topic_num:
        for i in dict[str(q)]:
            search_corpus.append(corpus_tfidf[i - 1])
            index_dict[index_num] = i
            index_num += 1

    for q in topic_num:
        file = "E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/topic/" + str(q) + ".index"
        if os.path.exists(file):
            index = similarities.MatrixSimilarity.load(file)
        else:
            index = similarities.MatrixSimilarity(lda[search_corpus])
            index.save(file)
    print('构建索引完成')
    sims = index[vector]
    print(sims)
    sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])
    # print(sorted_sims)
    df = pd.read_csv("E:/pycharm/judicial_doc_measurement/utils/lda/lda_model/raw_text.csv", encoding="utf-8", header=None)

    count = 0
    law_articles = []
    for doc in sorted_sims:
        content = df[1][index_dict[doc[0]]]
        law_article = df[2][index_dict[doc[0]]].split(';')
        # if keyword[0] not in content and keyword[1] not in content and keyword[2] not in content\
        # 		and keyword[3] not in content and keyword[4] not in content \
        # 		and keyword[5] not in content and keyword[6] not in content and keyword[7] not in content \
        # 		and keyword[8] not in content and keyword[9] not in content:
        # 	continue
        count += 1
        print("推荐案例%d 相似度：%f\n%s\n" % (index_dict[doc[0]], doc[1], content))
        law_articles.extend(law_article)
        if count == 10:  # 最相似的
            break
        print('相似案例法条\n%s'%(';'.join(law_articles)))
    return law_tmp,law_articles,
def law_index(file_path):
    law_tmp,law_articles = recommender(file_path)
    law_dic = list2dic(law_articles)
    count = 0
    print(law_tmp,law_articles)
    for i in law_tmp:
        for j in law_dic:
            if i==j:
                count+=1
    print('相似案件法条数目',count)
    if count == 0 and len(law_tmp) > 0:
        res= cf.law_articles_rational_base
    elif count>0:
        res= cf.law_articles_rational_subscore*count+cf.law_articles_rational_base
        if res>cf.law_articles_rational_score:
            res = cf.law_articles_rational_score
    else:
        res = 0
    a = sorted(law_dic.items(), key=lambda item: item[1],reverse=True)
    recommend_law = []
    for num in range(int(len(a)*0.3)):
        recommend_law.append(a[num])
    print(res)
    print(recommend_law)
    return res,recommend_law



def list2dic(lis):
    dic = {}
    for i in lis:
        if i in dic.keys():
            dic[i]+=1
        else:
            dic[i]=1
    return dic

if __name__=='__main__':
    # 预处理准备
    # alltext, anyou, law, path = data_preprocess()
    # # print(alltext)
    # raw_text_csv(alltext, anyou, law, path)
    # process_csv(alltext)

    #lda模型训练
    # lda()

    #相似文书法条推荐
    # recommender()
    file_path_test = "D:/NJU/final_project/data/example/0.xml"
    law_index(file_path_test)






