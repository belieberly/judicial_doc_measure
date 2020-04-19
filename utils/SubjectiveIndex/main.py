# 实际上是线程
from multiprocessing.dummy import Pool
# 多进程
# from multiprocessing import Pool
from xml.etree import ElementTree as etree
from utils.SubjectiveIndex.copy_detect import long_detect, levenshtein
import config as cf
from utils.SubjectiveIndex.sentiment_classify import sentiment_index as sentiment
from utils.SubjectiveIndex.sentiment_classify import sentiment_index1 as text_style
from utils.lda.lda import law_index
from config.log_config import logger


def text_style_classification(root_node):
    for node in root_node:
        if node.tag == 'AJJBQK':
            AJJBQK_txt = node.get('value')
    res, count = text_style(AJJBQK_txt)
    if len(res) == 0:
        return cf.sentiment_classify_score, res
    else:
        res_score = cf.text_style_classify_score - count * cf.text_style_classify_fault
    if res_score < 0:
        res_score = 0
    return res_score, res


def copy_detect_index(root_node):
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


def sentiment_index(root_node):
    for node in root_node:
        if node.tag == 'AJJBQK':
            AJJBQK_txt = node.get('value')
    res = sentiment(AJJBQK_txt)
    res_score = 0
    if len(res) == 0:
        return cf.sentiment_classify_score, res
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


def func_process1():
    return


def func_process2():
    return


def func_process(subject_score_dic, subject_score, process_res):
    law_articles_res = []
    sentiment_res = []
    text_style_res = []
    copy_detect_res = ''
    if 'copy_detect_index' in process_res.keys():
        score, res = process_res['copy_detect_index'].get()
        subject_score_dic['copy_detect_index'] = score
        subject_score += score
        copy_detect_res = res
    if 'sentiment_index' in process_res.keys():
        score, res = process_res['sentiment_index'].get()
        subject_score_dic['sentiment_index'] = score
        subject_score += score
        sentiment_res = res
    if 'text_style_classification' in process_res.keys():
        score, res = process_res['text_style_classification'].get()
        subject_score_dic['text_style_classification'] = score
        subject_score += score
        text_style_res = res
    if 'law_articles_rational' in process_res.keys():
        score, res = process_res['law_articles_rational'].get()
        subject_score_dic['law_articles_rational'] = score
        subject_score += score
        law_articles_res = res
    return law_articles_res, sentiment_res, text_style_res, copy_detect_res, subject_score_dic, subject_score


def subjective_measure(filepath, subject_list):
    pool = Pool()
    subject_score = 0
    subject_score_dic = {}
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    process_res = {}
    logger.info('subject' + str(subject_list) + '!!!!!!!!!!!!!!')
    if 'copy_detect_index' in subject_list:
        # tmp_score, copy_detect_res = copy_detect_index(root_node)
        # subject_score += tmp_score
        # subject_score_dic['copy_detect_index'] = [tmp_score, cf.copy_detect_score]
        process_res['copy_detect_index'] = pool.apply_async(copy_detect_index, (root_node,))
    else:
        subject_score += cf.copy_detect_score
        print('copy_dect:', cf.copy_detect_score)
    if 'sentiment_index' in subject_list:
        # tmp_score, sentiment_res = sentiment_index(root_node)
        process_res['sentiment_index'] = pool.apply_async(sentiment_index, (root_node,))
        # subject_score += tmp_score
        # subject_score_dic['sentiment_index'] = [tmp_score, cf.sentiment_classify_score]
    else:
        # subject_score_dic['sentiment_index'] = [cf.sentiment_classify_score, cf.sentiment_classify_score]
        subject_score += cf.sentiment_classify_score
        print('sentiment_index:', cf.sentiment_classify_score)
    if 'text_style_classification' in subject_list:
        process_res['text_style_classification'] = pool.apply_async(text_style_classification, (root_node,))
        # subject_score += tmp_score
        # subject_score_dic['text_style_classification'] = [tmp_score, cf.text_style_classify_score]
    else:
        # subject_score_dic['text_style_classification'] = [cf.text_style_classify_score,
        #                                                       cf.text_style_classify_score]
        subject_score += cf.text_style_classify_score
        print('text_style_classification:', cf.text_style_classify_score)
    if 'law_articles_rational' in subject_list:
        process_res['law_articles_rational'] = pool.apply_async(law_index, (filepath,))
        # tmp_score, law_articles_res = law_index(filepath)
        # subject_score += tmp_score
        # subject_score_dic['law_articles_rational'] = [tmp_score, cf.law_articles_rational_score]
    else:
        # if 'law_articles_rational_' not in index_dic.keys():
        #     subject_score_dic['law_articles_rational'] = [cf.law_articles_rational_score,
        #                                                   cf.law_articles_rational_score]
        subject_score += cf.law_articles_rational_score
        print('law_article_index:', cf.law_articles_rational_score)
    pool.close()
    pool.join()
    law_articles_res, sentiment_res, text_style_res, copy_detect_res, subject_score_dic, subject_score = func_process(
        subject_score_dic, subject_score, process_res)

    return subject_score, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res
#
#
# if __name__ == '__main__':
#     filepath = 'D:/NJU/final_project/data/example/0.xml'
#     wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': {}}
#     subject_index = {
#         "text_style_classification_": 1,
#         "sentiment_index_": 1,
#         "copy_detect_index_": 1,
#         "law_articles_rational_": 1
#     }
#     index_dic = {
#         "text_style_classification_": 1,
#         "sentiment_index_": 1,
#         "copy_detect_index_": 1,
#         "law_articles_rational_": 1
#     }
#     path_file = open('G:/judicial_data/民事一审案件.tar/民事一审案件/path_min_pan_filter_len.txt', 'r', encoding='utf-8')
#     res_file = open('../../data/subject.csv', 'w', encoding='utf-8')
#     count = 0
#     tmp = []
#     for path in path_file.readlines():
#         count += 1
#         if count > 101:
#             break
#         path = 'G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/' + path.strip()
#         print('待检测文书名称为：' + path)
#         subject_score, wenshu_corr, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res,res = subjective_measure(path, index_dic, subject_index, wenshu_corr)
#         print(subject_score)
#         tmp.append(res)
#         res_file.write('\t'.join(str(res)) + '\n')
#     c = np.array(tmp)
#     mean = c.mean(axis=0)
#     max = c.max(axis=0)
#     min = c.min(axis=0)
#     std = c.std(axis=0)
#     print(mean)
#     print(min)
#     print(max)
#     print(std)
