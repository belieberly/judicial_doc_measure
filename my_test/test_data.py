import json
from config import *
from flask import jsonify
names =locals()
index = {'met_CSR': '参诉人信息细致性', 'met_AJJBQK': '事实部分细致性', 'met_CPFXGC': '理由部分细致性',
         'del_date': '延迟性', 'aut_AY': '案由信息类别规范性', 'aut_CPYJ': '裁判依据引用规范性',
         'com_PJNR': '判决内容说明完整性', 'com_SFCD': '诉费承担说明完整性', 'con_num': '数字使用一致性',
         'con_pun': '标点符号使用一致性', 'rea_SSMS': '事实描述部分简明性', 'rea_ZYJD': '争议焦点条理性',
         'acc_GCSX': '构成事项准确性', 'acc_SLJG': '审理经过准确性', 'acc_CSR': '参诉人信息准确性',
         'text_style_classification': '语言风格鲜明性', 'sentiment_index': '客观程度',
         'copy_detect_index': '语言抄袭检测', 'law_articles_rational': '法条合理性'}


def test_date():
    inputf = open('./transfer_config.json','r',encoding='utf-8')
    config_json = json.load(inputf)
    file = open('./test_data.json','w',encoding = 'utf-8')
    my_config = []
    for index in config_json:
        label = index.strip('_')
        config_item = {"value": index, "label": names['index'][label], "component": "switch", "type": "number"}
        my_config.append(config_item)
    json.dump({'my_config':my_config},file,ensure_ascii=False)

test_date()
