from xml.etree import ElementTree as etree
import re
from utils.SubjectiveIndex.copy_detect import long_detect, levenshtein
import json
import config as cf
from utils.SubjectiveIndex.sentiment_classify import sentiment_index as sentiment
from utils.SubjectiveIndex.sentiment_classify import sentiment_index1 as text_style
import numpy as np
from utils.lda.lda import law_index


def text_style_classification(AJJBQK_txt):
    res = text_style(AJJBQK_txt)
    res_score = 0
    if len(res) == 0:
        return cf.sentiment_classify_score
    else:
        for tup in res:
            if tup[1] < cf.text_style_classify_threshold:
                res_score -= cf.text_style_classify_fault
        res_score += cf.text_style_classify_score
    if res_score < 0:
        res_score = 0
    return res_score, res


def copy_detect_index(root_node):
    res_score = 0
    copy_detect_res = []
    YGSCD_txt = ''
    BGBCD_txt = ''
    CMSSD_txt = ''
    for node in root_node:
        if node.tag == 'AJJBQK':
            for subnode in node:
                if subnode.tag == 'YGSCD':
                    YGSCD_txt = subnode.get('value')
                elif subnode.tag == 'BGBCD':
                    BGBCD_txt = subnode.get('value')
                elif subnode.tag == 'CMSSD':
                    CMSSD_txt = subnode.get('value')
    if len(YGSCD_txt) != 0 and len(CMSSD_txt) != 0:
        copy_subscore1, tmp_txt1 = long_detect(YGSCD_txt, CMSSD_txt)
        copy_detect_res.append(tmp_txt1)
    else:
        copy_subscore1 = cf.copy_detect_score
    if len(BGBCD_txt) != 0 and len(CMSSD_txt) != 0:
        copy_subscore2, tmp_txt2 = long_detect(BGBCD_txt, CMSSD_txt)
        copy_detect_res.append(tmp_txt2)
    else:
        copy_subscore2 = cf.copy_detect_score

    res_score = (copy_subscore1 + copy_subscore2) / 2.0
    return res_score, '\n'.join(copy_detect_res)


def sentiment_index(AJJBQK_txt):
    res = sentiment(AJJBQK_txt)
    res_score = 0
    if len(res) == 0:
        return cf.sentiment_classify_score
    else:
        for tup in res:
            if tup[1] > cf.sentiment_classify_threshold:
                res_score -= cf.sentiment_classify_fault
        res_score += cf.sentiment_classify_score
    if res_score < 0:
        res_score = 0
    return res_score, res


def law_articles_rational(filepath):
    return 0.7


# file_path = input('输入为评估文件名称').strip()
# filepath = 'D:/NJU/final_project/data/example/' + file_path
#
# subject_index = {'抄袭检测': 0, '法条合理性': 0, '文本风格度量（基于bert的分类）': 0}
# subject_index['抄袭检测'] = copy_detect_index(filepath)
# subject_index['文本风格度量（基于bert的分类）'] = text_style_classification(filepath)
# outfile = '../../report/test.json'

# with open(outfile, 'a+', encoding='utf-8') as f:
#     json.dump(subject_index, f, ensure_ascii=False)


def subjective_measure(filepath, index_dic, subject_index, wenshu_corr):
    subject_score = 0
    subject_score_dic = {}
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    law_articles_res = []
    sentiment_res = []
    text_style_res = []
    copy_detect_res = ''
    res = []
    if 'copy_detect_index_' in index_dic.keys() and index_dic['copy_detect_index_'] == 1:
        tmp_score, copy_detect_res = copy_detect_index(root_node)
        print('copy_dect:', tmp_score)
        subject_score += tmp_score
        res.append(tmp_score)
        subject_score_dic['copy_detect_index'] = [tmp_score, cf.copy_detect_score]
    else:
        if 'copy_detect_index_' not in index_dic.keys():
            subject_score_dic['copy_detect_index'] = [cf.copy_detect_score, cf.copy_detect_score]
        subject_score += cf.copy_detect_score
        print('copy_dect:', cf.copy_detect_score)
        res.append(cf.copy_detect_score)
    if 'sentiment_index_' in index_dic.keys() and index_dic['sentiment_index_'] == 1:
        tmp_score = cf.sentiment_classify_score
        for node in root_node:
            if node.tag == 'AJJBQK':
                AJJBQK_txt = node.get('value')
                tmp_score, sentiment_res = sentiment_index(AJJBQK_txt)
        subject_score += tmp_score
        print('sentiment_index:', tmp_score)
        res.append(tmp_score)
        subject_score_dic['sentiment_index'] = [tmp_score, cf.sentiment_classify_score]
    else:
        if 'sentiment_index_' not in index_dic.keys():
            subject_score_dic['sentiment_index'] = [cf.sentiment_classify_score, cf.sentiment_classify_score]
        subject_score += cf.sentiment_classify_score
        print('sentiment_index:', cf.sentiment_classify_score)
        res.append(cf.sentiment_classify_score)
    if 'text_style_classification_' in index_dic.keys() and index_dic['text_style_classification_'] == 1:
        tmp_score = cf.text_style_classify_score
        for node in root_node:
            if node.tag == 'AJJBQK':
                AJJBQK_txt = node.get('value')
                tmp_score, text_style_res = text_style_classification(AJJBQK_txt)
        subject_score += tmp_score
        print('text_style_classification:', tmp_score)
        res.append(tmp_score)
        subject_score_dic['text_style_classification'] = [tmp_score, cf.text_style_classify_score]
    else:
        if 'text_style_classification_' not in index_dic.keys():
            subject_score_dic['text_style_classification'] = [cf.text_style_classify_score,
                                                              cf.text_style_classify_score]
        subject_score += cf.text_style_classify_score
        print('text_style_classification:', cf.text_style_classify_score)
        res.append(cf.text_style_classify_score)
    if 'law_articles_rational_' in index_dic.keys() and index_dic['law_articles_rational_'] == 1:
        tmp_score,law_articles_res = law_index(filepath)
        subject_score += tmp_score
        print('law_article_index:', tmp_score)
        res.append(tmp_score)
        subject_score_dic['law_articles_rational'] = [tmp_score, cf.law_articles_rational_score]
    else:
        if 'law_articles_rational_' not in index_dic.keys():
            subject_score_dic['law_articles_rational'] = [cf.law_articles_rational_score,
                                                          cf.law_articles_rational_score]
        subject_score += cf.law_articles_rational_score
        print('law_article_index:', cf.law_articles_rational_score)
        res.append(cf.law_articles_rational_score)
    print(subject_score, wenshu_corr)
    return subject_score, wenshu_corr, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res,res


if __name__ == '__main__':
    filepath = 'D:/NJU/final_project/data/example/0.xml'
    wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': {}}
    subject_index = {
        "text_style_classification_": 1,
        "sentiment_index_": 1,
        "copy_detect_index_": 1,
        "law_articles_rational_": 1
    }
    index_dic = {
        "text_style_classification_": 1,
        "sentiment_index_": 1,
        "copy_detect_index_": 1,
        "law_articles_rational_": 1
    }
    path_file = open('G:/judicial_data/民事一审案件.tar/民事一审案件/path_min_pan_filter_len.txt', 'r', encoding='utf-8')
    res_file = open('../../data/subject.csv', 'w', encoding='utf-8')
    count = 0
    tmp = []
    for path in path_file.readlines():
        count += 1
        if count > 101:
            break
        path = 'G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/' + path.strip()
        print('待检测文书名称为：' + path)
        subject_score, wenshu_corr, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res,res = subjective_measure(path, index_dic, subject_index, wenshu_corr)
        print(subject_score)
        tmp.append(res)
        res_file.write('\t'.join(str(res)) + '\n')
    c = np.array(tmp)
    mean = c.mean(axis=0)
    max = c.max(axis=0)
    min = c.min(axis=0)
    std = c.std(axis=0)
    print(mean)
    print(min)
    print(max)
    print(std)

