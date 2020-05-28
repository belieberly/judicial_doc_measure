import json
from utils.ObjectiveIndex import main as obj_main
from utils.SubjectiveIndex import main as sub_main
import web_utils
import config as cf
from xml.etree import ElementTree as etree
import re
from config import *
# 加载logger配置
from config.log_config import logger

# 客观质量度量
# 输入为文书路径和指标字典
names = locals()


def get_report_json(index_list, object_score, object_score_dict, wenshu_content, index_res, subject_score,
                    wenshu_corr, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res,
                    province, writ_date):
    report = {}
    logger.info('----------------' + str(index_list) + '-------------')
    report['object_score'] = object_score
    report['subject_score'] = subject_score
    report['province'] = province
    report['writ_date'] = writ_date
    standard = ['文首', '首部', '事实', '理由', '依据', '主文', '尾部', '落款', '附件']
    # 报告度量项，必须包含
    report['metrics'] = []
    for metric in index_list:
        report['metrics'].append(cf.index[metric])
    report['pzwzx'] = []
    if len(index_res) != 0:
        for i in range(len(standard)):
            report['pzwzx'].append({'name': standard[i], 'score': index_res[i]})
    # 详细说明部分，也必须要有
    report['xxsm'] = []
    for par in wenshu_content:
        if wenshu_content[par] != '':
            report['xxsm'].append({'content': wenshu_content[par], 'advice': wenshu_corr[par]})
    # 建立所有指标类的字典列表
    obj_index_cat = {}
    for index_name in object_score_dict:
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
                                                 {'metric': names['index'][index_name],
                                                  'score': object_score_dict[index_name][0],
                                                  'total': object_score_dict[index_name][1]}]}
    if 'met' in obj_index_cat.keys():
        report['xzx'] = {'name': '细致性', 'content': obj_index_cat['met']}
    if 'del' in obj_index_cat.keys():
        report['ycx'] = {'name': '延迟性', 'content': obj_index_cat['del']}
    # for key in obj_index_cat:
    #     report[key] = {'name':names['index_cat'][key],'content':obj_index_cat[index]}
    if len(obj_index_cat) > 4:
        report['radar'] = []
        for i in obj_index_cat:
            radar_i = {'metric': names['index_cat'][i], 'score': obj_index_cat[i]['cat_score'],
                       'total': obj_index_cat[i]['tol_score']}
            report['radar'].append(radar_i)
    if 'copy_detect_index' in subject_score_dic.keys():
        report['cxjc'] = {'score': subject_score_dic['copy_detect_index'], 'total': cf.copy_detect_score,
                          'conclusion': copy_detect_res}
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
    # 每个度量指标的得分情况
    object_score_dict.update(subject_score_dic)
    report['index_dic'] = object_score_dict
    return report


def get_report_info(filepath):
    province = ''
    writ_date = ''
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    for node in root_node:
        if node.tag == 'WS':
            WS_txt = node.get('value').strip()
            print(WS_txt)
            if re.match(r'(北京市|广东省|山东省|江苏省|河南省|上海市|河北省|浙江省|陕西省|湖南省|重庆市|福建省|天津市|云南省|四川省|广西壮族自治区|安徽省|海南省|江西省|'
                        r'湖北省|山西省|辽宁省|黑龙江|内蒙古自治区|贵州省|甘肃省|青海省|新疆维吾尔自治区|西藏区|吉林省|宁夏回族自治区).*', WS_txt):
                # 获取地点
                province = re.match(
                    r'(北京市|广东省|山东省|江苏省|河南省|上海市|河北省|浙江省|陕西省|湖南省|重庆市|福建省|天津市|云南省|四川省|广西壮族自治区|安徽省|海南省|江西省|'
                    r'湖北省|山西省|辽宁省|黑龙江|内蒙古自治区|贵州省|甘肃省|青海省|新疆维吾尔自治区|西藏区|吉林省|宁夏回族自治区).*',
                    WS_txt).group(1)
                # 获取时间
            if re.match(r'.*（([0-9]{4})）.{0,8}初字第[0-9]{0,6}号', WS_txt):
                writ_date = re.match(r'.*（([0-9]{4})）.{0,8}初字第[0-9]{0,6}号', WS_txt).group(1)
    print(province, writ_date)
    return province, writ_date


def doc_measure(filepath, input_index_dic):
    wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': {}}

    # 抽出所有需要检测的指标
    subject_list, object_list, index_list = web_utils.get_index(input_index_dic)
    object_score, wenshu_corr, object_score_dict, wenshu_content, index_res = obj_main.objective_measure(filepath,
                                                                                                         object_list,
                                                                                                         wenshu_corr)
    subject_score, subject_score_dic, law_articles_res, sentiment_res, text_style_res, copy_detect_res = \
        sub_main.subjective_measure(filepath, subject_list)
    print(object_index)
    province, writ_date = get_report_info(filepath)
    json_res = get_report_json(index_list, object_score, object_score_dict, wenshu_content, index_res,
                               subject_score, wenshu_corr, subject_score_dic, law_articles_res, sentiment_res,
                               text_style_res, copy_detect_res, province, writ_date)

    return json_res, province, writ_date



#
# if __name__ == '__main__':
#     filepath = 'D:/NJU/final_project/data/example/0.xml'
#     input_index_dict = {
#         "met_CSR": 0,
#         "met_AJJBQK": 1,
#         "met_CPFXGC": 1,
#         "del_date": 1,
#         "aut_AY": 1,
#         "aut_CPYJ": 1,
#         "com_PJNR": 1,
#         "com_SFCD": 1,
#         "con_num": 1,
#         "con_pun": 0,
#         "rea_SSMS": 1,
#         "rea_ZYJD": 1,
#         "acc_GCSX": 1,
#         "acc_SLJG": 1,
#         "acc_CSR": 1,
#         "text_style_classification": 0,
#         "sentiment_index": 1,
#         "copy_detect_index": 1,
#         "law_articles_rational": 0
#     }
#     doc_measure(filepath, input_index_dict)
