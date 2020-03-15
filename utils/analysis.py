# 得到分析报告
from config import *
import config as cf
import json

names = locals()


def task_report(report_path_list, index_dic):
    task_report = {'multiradar': {}, 'avg_score':{},'vs_standard': {'test_value': [], 'standard_value': []}, 'multi_radar': []}
    task_report['metrics'] = []
    for metric in index_dic:
        metric = metric.strip('_')
        task_report['metrics'].append(cf.index[metric])
    length = len(report_path_list)
    for report_path in report_path_list:
        report_file = open(report_path, 'r', encoding='utf-8')
        report_json = json.load(report_file)
        if 'radar' in report_json.keys():
            if len(task_report['multiradar']) == 0:
                for metric in report_json['radar']:
                    task_report['multiradar'][metric['metric']] = {'score': metric['score'], 'total': metric['total']}
            else:
                for metric in report_json['radar']:
                    task_report['multiradar'][metric['metric']]['score'] += metric['score']
                    task_report['multiradar'][metric['metric']]['total'] += metric['total']
        if len(task_report['avg_score']) == 0:
            for index in report_json['index_dic']:
                index = index.strip('_')
                task_report['avg_score'][index] = {'score': report_json['index_dic'][index][0]}
        else:
            for index in report_json['index_dic']:
                index = index.strip('_')
                task_report['avg_score'][index]['score'] += report_json['index_dic'][index][0]
    for metric in task_report['multiradar']:
        task_report['multiradar'][metric]['score'] /= length
        task_report['multiradar'][metric]['total'] /= length
        task_report['multi_radar'].append({'metric': metric, 'score': task_report['multiradar'][metric]['score'],
                                      'total': task_report['multiradar'][metric]['total']})
    for index in task_report['avg_score']:
        task_report['avg_score'][index]['score'] /= length
        task_report['vs_standard']['test_value'].append(task_report['avg_score'][index]['score'])
        task_report['vs_standard']['standard_value'].append(names['standard_value'][index])
    task_report['vs_standard']['x_axis'] = task_report['metrics']
    outputf = open('../test_task_report.json', 'w', encoding='utf-8')
    json.dump(task_report, outputf, ensure_ascii=False)


if __name__ == '__main__':
    report_path_list = [
        'E:/pycharm/judicial_doc_measurement/web_data/writ_report/13309ee2-ed68-4628-a8cf-44f14eec441d.json',
        'E:/pycharm/judicial_doc_measurement/web_data/writ_report/21de5e9e-17f7-447f-bf77-61b6aee0b08a.json']
    index_dic = {
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
    task_report(report_path_list, index_dic)
