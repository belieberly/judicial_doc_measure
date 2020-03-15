import json
from utils.ObjectiveIndex import main as obj_main
from utils.SubjectiveIndex import main as sub_main
from web_utils import __init__
import config as cf
from xml.etree import ElementTree as etree
import re
from config import *

# 客观质量度量
# 输入为文书路径和指标字典
names = locals()


def get_report_json(index_dic, object_score, object_score_dict, wenshu_content, index_res, subject_score,
                    wenshu_corr, subject_score_dic, law_articles_res, sentiment_res, text_style_res):
    report = {}
    report['object_score'] = object_score
    report['subject_score'] = subject_score
    standard = ['文首', '首部', '事实', '理由', '依据', '主文', '尾部', '落款', '附件']
    report['metrics'] = []
    for metric in index_dic:
        metric = metric.strip('_')
        report['metrics'].append(cf.index[metric])
    report['pzwzx'] = []
    for i in range(len(standard)):
        report['pzwzx'].append({'name':standard[i],'score': index_res[i]})
    report['xxsm'] = []
    for par in wenshu_content:
        if wenshu_content[par] != '':
            report['xxsm'].append({'content': wenshu_content[par], 'advice': wenshu_corr[par]})
    # 建立所有指标的字典列表
    obj_index_cat = {}
    for index_name in object_score_dict:
        index_name = index_name.strip('_')
        index_tol_name = index_name.split('_', 2)[0]
        if index_tol_name in obj_index_cat.keys():
            obj_index_cat[index_tol_name]['cat_score'] += object_score_dict[index_name][0]
            obj_index_cat[index_tol_name]['tol_score'] += object_score_dict[index_name][1]
            obj_index_cat[index_tol_name]['submetric'].append(
                {'metric': names['index'][index_name], 'score': object_score_dict[index_name][0],
                 'total': object_score_dict[index_name][1]})
        else:
            obj_index_cat[index_tol_name] = {'cat_score': object_score_dict[index_name][0],
                                             'tol_score': object_score_dict[index_name][1],
                                             'submetric': [
                                                 {'metric': names['index'][index_name], 'score': object_score_dict[index_name][0],
                                                  'total': object_score_dict[index_name][1]}]}
    if 'met' in obj_index_cat.keys():
        report['xzx'] = {'name':'细致性','content': obj_index_cat['met']}
    if 'del' in obj_index_cat.keys():
        report['ycx'] = {'name':'延迟性','content':obj_index_cat['del']}
    # for key in obj_index_cat:
    #     report[key] = {'name':names['index_cat'][key],'content':obj_index_cat[index]}
    if len(obj_index_cat) > 4:
        report['radar'] = []
        for i in obj_index_cat:
            index_tol_name  = i.strip('_')
            radar_i = {'metric': names['index_cat'][index_tol_name], 'score': obj_index_cat[i]['cat_score'],
                       'total': obj_index_cat[i]['tol_score']}
            report['radar'].append(radar_i)
    if 'copy_detect_index' in subject_score_dic.keys():
        report['cxjc'] = {'score': subject_score_dic['text_style_classification'][0], 'total': cf.copy_detect_score}
    if 'text_style_classification' in subject_score_dic.keys():
        report['yyfg'] = []
        for sentence in text_style_res:
            sentence_ = {'sentence': sentence[0], 'delta': sentence[1]}
            report['yyfg'].append(sentence_)
    if 'sentiment_index' in subject_score_dic.keys():
        report['kgcd'] = []
        for sentence in sentiment_res:
            sentence_ = {'sentence': sentence[0], 'delta': sentence[1]}
            report['kgcd'].append(sentence_)
    if 'law_articles_rational' in subject_score_dic.keys():
        report['xsal'] = law_articles_res
    # outputfile = open('../data/test_report.json', 'w', encoding='utf-8')
    # json.dump(report, outputfile, ensure_ascii=False)
    object_score_dict.update(subject_score_dic)
    report['index_dic'] = object_score_dict
    return report


def get_report_info(filepath):
    province = ''
    writ_date = ''
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    flag = 0
    for node in root_node:
        if node.tag == 'WS':
            WS_txt = node.get('value').strip()
            print(WS_txt)
            if re.match(r'(北京市|广东省|山东省|江苏省|河南省|上海市|河北省|浙江省|陕西省|湖南省|重庆市|福建省|天津市|云南省|四川省|广西壮族自治区|安徽省|海南省|江西省|'
                        r'湖北省|山西省|辽宁省|黑龙江|内蒙古自治区|贵州省|甘肃省|青海省|新疆维吾尔自治区|西藏区|吉林省|宁夏回族自治区).{1,10}人民法院 民事判决书 '
                        r'（([0-9]{4})）.{0,8}初字第[0-9]{0,6}号', WS_txt):
                # 获取地点
                province = re.match(
                    r'(北京市|广东省|山东省|江苏省|河南省|上海市|河北省|浙江省|陕西省|湖南省|重庆市|福建省|天津市|云南省|四川省|广西壮族自治区|安徽省|海南省|江西省|'
                    r'湖北省|山西省|辽宁省|黑龙江|内蒙古自治区|贵州省|甘肃省|青海省|新疆维吾尔自治区|西藏区|吉林省|宁夏回族自治区).{1,10}人民法院 民事判决书 （([0-9]{4})）.{0,8}初字第[0-9]{0,6}号',
                    WS_txt).group(1)
                # 获取时间
                writ_date = re.match(
                    r'(北京市|广东省|山东省|江苏省|河南省|上海市|河北省|浙江省|陕西省|湖南省|重庆市|福建省|天津市|云南省|四川省|广西壮族自治区|安徽省|海南省|江西省|'
                    r'湖北省|山西省|辽宁省|黑龙江|内蒙古自治区|贵州省|甘肃省|青海省|新疆维吾尔自治区|西藏区|吉林省|宁夏回族自治区).{1,10}人民法院 民事判决书 （([0-9]{4})）.{0,8}初字第[0-9]{0,6}号',
                    WS_txt).group(2)
    return province,writ_date


def doc_measure(filepath, input_index_dic):
    target_file = open(cf.transfer_config_path,'r',encoding = 'utf-8')
    target_index = json.load(target_file)
    # 输入的文书指标和标准指标
    index_dic = __init__.write_intersect_properties(input_index_dic, target_index)
    wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': {}}
    object_index = {"met_CSR_": 1,
                    "met_AJJBQK_": 1,
                    "met_CPFXGC_": 1,
                    "del_date_": 1,
                    "aut_AY_": 1,
                    "aut_CPYJ_": 1,
                    "com_PJNR_": 1,
                    "com_SFCD_": 1,
                    "con_num_": 1,
                    "con_pun_": 1,
                    "rea_SSMS_": 1,
                    "rea_ZYJD_": 1,
                    "acc_GCSX_": 1,
                    "acc_SLJG_": 1,
                    "acc_CSR_": 1, }
    subject_index = {
        "text_style_classification_": 1,
        "sentiment_index_": 1,
        "copy_detect_index_": 1,
        "law_articles_rational_": 1
    }
    # 和客观指标取交集
    object_dic = __init__.write_intersect_properties(index_dic, object_index)
    # 和主观指标取交集
    subject_dic = __init__.write_intersect_properties(index_dic, subject_index)

    object_score, wenshu_corr, object_score_dict, wenshu_content, index_res = obj_main.objective_measure(filepath,
                                                                                                         object_dic,
                                                                                                         object_index,
                                                                                                         wenshu_corr)
    subject_score, wenshu_corr, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res = sub_main.subjective_measure(
        filepath, subject_dic, subject_index, wenshu_corr)

    json_res = get_report_json(index_dic, object_score, object_score_dict, wenshu_content, index_res,
                               subject_score, wenshu_corr, subject_score_dic, law_articles_res, sentiment_res,
                               text_style_res)
    province,writ_date = get_report_info(filepath)
    return json_res,province,writ_date

#多个文书
# def docs_measure(filepath_list,input_index_dict):
#     reports = []
#     for filepath in filepath_list:
#         report = {}
#         json_res,province,writ_date = doc_measure(filepath,input_index_dict)
#         report['json']=json_res
#         report['']


if __name__ == '__main__':
    filepath = 'D:/NJU/final_project/data/example/0.xml'
    input_index_dict = {
        "met_CSR_": 1,
        "met_AJJBQK_": 1,
        "met_CPFXGC_": 1,
        "del_date_": 1,
        "aut_AY_": 1,
        "aut_CPYJ_": 1,
        "com_PJNR_": 1,
        "com_SFCD_": 1,
        "con_num_": 1,
        "con_pun_": 1,
        "rea_SSMS_": 1,
        "rea_ZYJD_": 1,
        "acc_GCSX_": 1,
        "acc_SLJG_": 1,
        "acc_CSR_": 1,
        "text_style_classification_": 1,
        "sentiment_index_": 1,
        "copy_detect_index_": 1,
        "law_articles_rational_": 1
    }
    doc_measure(filepath,input_index_dict)
