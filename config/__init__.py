# MySQL connection
# DB_URI = 'mysql+mysqldb://{}:{}@{}/{}.format(USERNAME，PASSWORD，HOSTNAME，PORT，DATABASE)'
import os

DevConfig = {
    'DEBUG': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'CELERY_ACCEPT_CONTENT': ['pickle', 'json', 'msgpack', 'yaml'],
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:ilynsm77@localhost:3306/judicial_doc_measurement',
    'BROKER_URL': 'redis://localhost:6379/0',
    'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0'
}

usr_cwd = 'E:/pycharm/judicial_doc_measurement'
web_data_path = os.path.join(usr_cwd, 'web_data')
# 上传文件默认路径
upload_base_dir = web_data_path + '/upload_files/'

# 报告保存默认路径
writ_report_base_dir = web_data_path + '/writ_report/'

# 分析报告默认路径
task_report_base_dir = web_data_path + '/task_report/'

# 标准指标字典json路径
transfer_config_path = os.path.join(usr_cwd, 'config/transfer_config.json')

# 客观度量指标
# objective_index = {'细致性': {'参诉人信息细致性': 'met_CSR', '事实部分细致性': 'met_AJJBQK', '理由部分细致性': 'met_CPFXGC'},
#                    '延迟性': {'案件信息延迟性': 'del_date', '裁判文书延迟性': 'del_date'},
#                    '真实性': {'案由信息类别规范性': 'aut_AY', '裁判依据引用规范性': 'aut_CPYJ'},
#                    '完整性': {'判决内容说明完整性': 'com_PJNR', '诉费承担说明完整性': 'com_SFCD'},
#                    '一致性': {'数字使用一致性': 'con_num', '标点符号使用一致性': 'con_pun'},
#                    '易读性': {'事实描述部分简明性': 'rea_SSMS', '争议焦点条理性': 'rea_ZYJD'},
#                    '准确性': {'构成事项准确性': 'acc_GCSX', '审理经过准确性': 'acc_SLJG', '参诉人信息准确性': 'acc_DSR'}}
# subjective_index = {'语言风格': {'语言风格辨析': 'text_style_classification', '情感倾向性': 'sentiment_index', '语言重构检测': 'copy_detect_index'},
#                     '法条合理性': {'基于相似案例': 'law_articles_rational'}}

objective_index = {'met_CSR': '参诉人信息细致性', 'met_AJJBQK': '事实部分细致性', 'met_CPFXGC': '理由部分细致性',
                   'del_date': '延迟性', 'aut_AY': '案由信息类别规范性', 'aut_CPYJ': '裁判依据引用规范性',
                   'com_PJNR': '判决内容说明完整性', 'com_SFCD': '诉费承担说明完整性', 'con_num': '数字使用一致性',
                   'con_pun': '标点符号使用一致性', 'rea_SSMS': '事实描述部分简明性', 'rea_ZYJD': '争议焦点条理性',
                   'acc_GCSX': '构成事项准确性', 'acc_SLJG': '审理经过准确性', 'acc_DSR': '参诉人信息准确性'}
subjective_index = {'text_style_classification': '语言风格鲜明性', 'sentiment_index': '情感倾向性',
                    'copy_detect_index': '语言重构检测', 'law_articles_rational': '法条合理性'}

index = {'met_CSR': '参诉人信息细致性', 'met_AJJBQK': '事实部分细致性', 'met_CPFXGC': '理由部分细致性',
         'del_date': '延迟性', 'aut_AY': '案由信息类别规范性', 'aut_CPYJ': '裁判依据引用规范性',
         'com_PJNR': '判决内容说明完整性', 'com_SFCD': '诉费承担说明完整性', 'con_num': '数字使用一致性',
         'con_pun': '标点符号使用一致性', 'rea_SSMS': '事实描述部分简明性', 'rea_ZYJD': '争议焦点条理性',
         'acc_GCSX': '构成事项准确性', 'acc_SLJG': '审理经过准确性', 'acc_CSR': '参诉人信息准确性',
         'text_style_classification': '语言风格鲜明性', 'sentiment_index': '客观程度',
         'copy_detect_index': '语言抄袭检测', 'law_articles_rational': '法条合理性'}

standard_value = {'met_CSR': 4.9, 'met_AJJBQK': 4.9, 'met_CPFXGC': 4.45,
                  'del_date': 3.69, 'aut_AY': 4.82, 'aut_CPYJ': 5,
                  'com_PJNR': 2.89, 'com_SFCD': 3.17, 'con_num': 9.75,
                  'con_pun': 5.57, 'rea_SSMS': 3.8, 'rea_ZYJD': 2.52,
                  'acc_GCSX': 8.19, 'acc_SLJG': 6.45, 'acc_CSR': 2.54,
                  'text_style_classification': 5.2, 'sentiment_index': 9.2,
                  'copy_detect_index': 9.44, 'law_articles_rational': 20}

index_cat = {'met': '细致性', 'del': '延迟性', 'aut': '真实性', 'com': '完整性', 'con': '一致性', 'rea': '易读性', 'acc': '完整性'}
# 细致性阈值
met_CSR_threshold = 7
met_AJJBQK_threshold = 5
met_CPFXGC_threshold = 8
# 细致性每项得分
met_subscore = 5
met_CSR_score = 5
met_AJJBQK_score = 5
met_CPFXGC_score = 5

# 抄袭检测分项总分
copy_detect_score = 25
# 抄袭检测相似度阈值
copy_detect_threshold = 0.7
# 抄袭检测每句扣分
copy_detect_fault = 5

# 文书情感分项总分
sentiment_classify_score = 25
# 文书情感单句阈值
sentiment_classify_threshold = 0.4
# 情感单句扣分
sentiment_classify_fault = 5

# 文书风格分项总分
text_style_classify_score = 25
# 文书风格单句阈值
text_style_classify_threshold = 0.8
# 文书风格单句扣分
text_style_classify_fault = 5

# 文书法条相关性
law_articles_rational_score = 25
law_articles_rational_base = 10
law_articles_rational_subscore = 5

# 文书信息延迟性得分
del_date_score = 10
del_date_subsocre1 = 5
del_date_subscore2 = 3
del_date_subscore3 = 1

# 案件信息延迟性阈值
del_date_AJXX_threshold1 = 1000
del_date_AJXX_threshold2 = 3000

# 文书信息延迟性阈值
del_date_WSXX_threshold1 = 100
del_date_WSXX_threshold2 = 200

# 案由信息类别规范性
aut_AY_score = 5

# 裁判依据引用规范性
aut_CPYJ_score = 5

# 标点符号使用一致性
con_pun_score = 10

# 数字使用一致性
con_num_score = 10
con_num_subscore = 5

# 判决内容说明完整性
com_PJNR_score = 5

# 诉费承担说明完整性
com_SFCD_score = 5

# 争议焦点条理性
rea_ZYJD_score = 5

# 构成事项准确性
acc_GCSX_score = 10
acc_GCSX_subscore1 = 2
acc_GCSX_subscore2 = 1

# 审理经过准确性
acc_SLJG_score = 10
acc_SLJG_subscore1 = 2
acc_SLJG_subscore2 = 1

# 参诉人信息准确性
acc_CSR_score = 5
acc_CSR_subscore1 = 0.5
acc_CSR_subscore2 = 0.25

# 事实描述部分简明性
rea_SSMS_score = 5
rea_SSMS_subscore = 1
rea_YGSCD_threshold = 381
rea_BGBCD_threshold = 187
rea_CMSSD_threshold = 613
rea_ZJD_threshold = 200
