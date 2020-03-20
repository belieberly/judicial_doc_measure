import _thread

from flask import Blueprint, request
from database.models import db, JudicialDoc, Report, Task, AnalysisReport
import json
import config as cf
import uuid
from utils import measure
from utils import analysis

import web_utils

blueprint_task_report = Blueprint('task_report', __name__)


@blueprint_task_report.route('./task', methods=['GET'])
def build_task():
    # 前端传入参数
    writ_id_list = request.values.get('writ-id-list')
    task_name = request.values.get('task-name')
    input_index_dic = {
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
    try:
        _thread.start_new_thread(task_measure, (writ_id_list, input_index_dic, task_name))
    except:
        print('创建任务进程失败')
    return '在创建啦'


def task_measure(writ_id_list, input_index_dic, task_name):
    tmp_task_uuid = str(uuid.uuid4())
    task = Task(id=tmp_task_uuid, user_id=web_utils.get_userid(), name=task_name)
    report_path_list = []
    province_dic = {}
    writ_date_dic = {}
    for writ_id in writ_id_list:
        writ = JudicialDoc.query.get(writ_id)
        print(writ)
        writ.task_id = tmp_task_uuid
        filepath = writ.loc
        file_name = writ.docname
        file_date = web_utils.time2timestamp(writ.date)
        print(file_date)
        report_json, province, writ_date = measure.doc_measure(filepath, input_index_dic)
        report_json['title'] = file_name
        report_json['time'] = file_date
        report_file_path = cf.writ_report_base_dir + writ_id + '.json'
        report_file = open(report_file_path, 'w', encoding='utf-8')
        json.dump(report_json, report_file, ensure_ascii=False)
        report_path_list.append(report_file_path)
        tmp_uuid = str(uuid.uuid4())
        report = Report(id=tmp_uuid, doc_id=writ_id, report_loc=report_file_path)
        db.session.add(report)
        writ.check_status = 'finished'
        if province != '':
            writ.province = province
            if province in province_dic.keys():
                province_dic[province] += 1
            else:
                province_dic[province] == 1
        if writ_date != '':
            writ.writ_date = writ_date
            if writ_date in writ_date_dic.keys():
                writ_date_dic[writ_date] += 1
            else:
                writ_date_dic[writ_date] == 1
        db.session.commit()
    db.session.add(task)
    task_report_json = analysis.task_report(report_path_list)
    task_report_loc = cf.task_report_base_dir + tmp_task_uuid + '.json'
    task_report_file = open(task.loc)
    json.dump(task_report_json, task_report_file, ensure_ascii=False)
    tmp_analysis_id = str(uuid.uuid4())
    analysis_report = AnalysisReport(id=tmp_analysis_id, task_id=tmp_task_uuid, loc=task_report_loc)
    db.session.add(analysis_report)
    db.session.commit()
    return 'build success'


@blueprint_task_report.route('/task_report', methods=['GET'])
def get_task_report():
    task_id = request.values.get('task-id')
    print(task_id)
    report = AnalysisReport.query.get(task_id=task_id)
    report_file = open(report.loc, 'r', encoding='utf-8')
    report_json = json.load(report_file)
    return report_json
