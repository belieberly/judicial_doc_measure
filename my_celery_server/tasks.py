

from my_celery_server import celery_server
from database.models import db, JudicialDoc, Report, Task, AnalysisReport
from utils import measure
from utils import analysis
import web_utils
import config as cf
import uuid
import json
from config.log_config import logger

# from multiprocessing import current_process
# current_process()._config = {'semprefix': '/mp'}

@celery_server.task(name="flask_app_context")
def flask_app_context():
    """
    celery使用Flask上下文
    :return:
    """
    from flask import current_app
    with current_app.app_context():
        print(current_app.name)
        result = str(current_app.config)
        print(result)
        return result


@celery_server.task(name="doc_measure_thread")
def doc_measure_thread(writ_id: str, input_index_dic: dict):
    print('调用了doc_measure函数')
    writ = JudicialDoc.query.get(writ_id)
    writ.check_status = 'ongoing'
    db.session.commit()
    print(writ)
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
    tmp_uuid = str(uuid.uuid4())
    report = Report(id=tmp_uuid, doc_id=writ_id, loc=report_file_path)
    db.session.add(report)
    db.session.commit()
    writ.check_status = 'finished'
    if province != '':
        writ.province = province
    if writ_date != '':
        writ.writ_date = writ_date
    db.session.commit()
    return


@celery_server.task(name="task_measure_thread")
def task_measure(writ_id_list, input_index_dic, task_name, tmp_task_uuid, task_date):
    task = Task.query.get(tmp_task_uuid)
    task.progress_status = 'ongoing'
    db.session.commit()
    report_path_list = []
    province_dic = {}
    writ_date_dic = {}
    try:
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
            # with自动close文件，不会出现截断的情况
            with open(report_file_path, 'w', encoding='utf-8') as report_file:
                json.dump(report_json, report_file, ensure_ascii=False)
            report_path_list.append(report_file_path)
            tmp_uuid = str(uuid.uuid4())
            report = Report(id=tmp_uuid, doc_id=writ_id, loc=report_file_path)
            db.session.add(report)
            writ.check_status = 'finished'
            if province != '':
                writ.province = province
                if province in province_dic.keys():
                    province_dic[province] += 1
                else:
                    province_dic[province] = 1
            if writ_date != '':
                writ.writ_date = writ_date
                if writ_date in writ_date_dic.keys():
                    writ_date_dic[writ_date] += 1
                else:
                    writ_date_dic[writ_date] = 1
            db.session.commit()
        task_report_json = analysis.task_report(report_path_list, input_index_dic, task_name, tmp_task_uuid, task_date)
        task_report_loc = cf.task_report_base_dir + tmp_task_uuid + '.json'
        task_report_file = open(task_report_loc,'w',encoding='utf-8')
        json.dump(task_report_json, task_report_file, ensure_ascii=False)
        tmp_analysis_id = str(uuid.uuid4())
        analysis_report = AnalysisReport(id=tmp_analysis_id, task_id=tmp_task_uuid, loc=task_report_loc)
        db.session.add(analysis_report)
        task.progress_status = 'finished'
        db.session.commit()

    except Exception as e:
        logger.info(e)
        task.progress_status = 'failed'
        db.session.commit()
