# 得到分析报告
import web_utils
from config import *
import config as cf
import json

names = locals()


def dic_convert(list):
    dic_res = {}
    for i in list:
        if i in dic_res.keys():
            dic_res[i] += 1
        else:
            dic_res[i] = 1
    return dic_res


def task_report(report_path_list, index_dic, task_name, tmp_task_uuid, task_date):
    task_report = {'writ_num': len(report_path_list), 'task_name': task_name,
                   'task_time': web_utils.time2timestamp(task_date) * 1000, 'vs_standard_distribution': {'series': []},
                   'radar': [], 'avg_score': {}, 'location_distribution': {}, 'time_distribution': {}, 'detail': []}
    standard_value = []
    test_value = []
    radar_raw_data = {}
    task_report['metrics'] = []
    for metric in index_dic:
        metric = metric.strip('_')
        task_report['metrics'].append(cf.index[metric])
    length = len(report_path_list)
    subject_score_list = []
    object_score_list = []
    province_list = []
    writ_date_list = []
    for report_path in report_path_list:
        with open(report_path, 'r', encoding='utf-8') as report_file:
            report_json = json.load(report_file)
        task_report['detail'].append(report_json)
        subject_score_list.append(report_json['subject_score'])
        object_score_list.append(report_json['object_score'])
        if report_json['province'] != '':
            province_list.append(report_json['province'])
        if report_json['writ_date'] != '':
            writ_date_list.append(report_json['writ_date'])
        if 'radar' in report_json.keys():
            if len(radar_raw_data) == 0:
                for metric in report_json['radar']:
                    radar_raw_data[metric['metric']] = {'score': metric['score'], 'total': metric['total']}
            else:
                for metric in report_json['radar']:
                    radar_raw_data[metric['metric']]['score'] += metric['score']
                    radar_raw_data[metric['metric']]['total'] += metric['total']
        if len(task_report['avg_score']) == 0:
            for index in report_json['index_dic']:
                index = index.strip('_')
                try:
                    task_report['avg_score'][index] = {'score': report_json['index_dic'][index][0],
                                                       'metric': cf.index[index]}
                except:
                    task_report['avg_score'][index] = {'score': report_json['index_dic'][index],
                                                       'metric': cf.index[index]}
        else:
            for index in report_json['index_dic']:
                index = index.strip('_')
                try:
                    task_report['avg_score'][index]['score'] += report_json['index_dic'][index][0]
                except:
                    task_report['avg_score'][index]['score'] += report_json['index_dic'][index]
    province_dic = dic_convert(province_list)
    time_dic = dic_convert(writ_date_list)
    task_report['location_distribution'] = {'x_axis_data': list(province_dic.keys()),
                                            'series': [{'name': '文书量', 'data': list(province_dic.values())}]}
    task_report['time_distribution'] = {'x_axis_data': list(map(lambda x: str(x) + '年', time_dic.keys())),
                                        'series': [{'name': '文书量', 'data': list(time_dic.values())}]}
    subject_score_avg = sum(subject_score_list) / len(subject_score_list)
    object_score_avg = sum(object_score_list) / len(object_score_list)
    task_report['subject_score_avg'] = round(subject_score_avg, 2)
    task_report['object_score_avg'] = round(object_score_avg, 2)
    task_report['score_avg'] = round((subject_score_avg + object_score_avg) / 2.0, 2)
    for metric in radar_raw_data:
        radar_raw_data[metric]['score'] /= length
        radar_raw_data[metric]['total'] /= length
        task_report['radar'].append({'metric': metric, 'score': radar_raw_data[metric]['score'],
                                     'total': radar_raw_data[metric]['total']})
    for index in task_report['avg_score']:
        task_report['avg_score'][index]['score'] /= length
        test_value.append(task_report['avg_score'][index]['score'])
        standard_value.append(names['standard_value'][index])
    task_report['vs_standard_distribution']['series'].append({'name': '待测数据集指标得分', 'data': test_value})
    task_report['vs_standard_distribution']['series'].append({'name': '标准数据集指标得分', 'data': standard_value})
    task_report['vs_standard_distribution']['x_axis_data'] = task_report['metrics']
    # with open('../web_data/task_report/' + tmp_task_uuid + '.json', 'w', encoding='utf-8') as outputf:
    #     json.dump(task_report, outputf, ensure_ascii=False)
    return task_report


if __name__ == '__main__':
    report_path_list = [
        'E:/pycharm/judicial_doc_measurement/web_data/writ_report/b799e9c9-ede1-4243-ab28-b3d1ea7c1e4e.json',
        'E:/pycharm/judicial_doc_measurement/web_data/writ_report/2e5ca696-7d11-4aa7-b9a0-6183bf41c094.json']
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
