from my_celery import my_celery_app
from database.models import db, JudicialDoc, Report
from utils import measure
import web_utils
import config as cf
import uuid
import json


@my_celery_app.task
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
    print(current_app.name)


@my_celery_app.task()
def doc_measure_thread(writ_id, input_index_dic):
    # from flask import current_app
    print('diaoyongrenwu')
    with current_app.app_context():
        print('调用了这个函数')
        writ = JudicialDoc.query.get(writ_id)
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
        report = Report(id=tmp_uuid, doc_id=writ_id, report_loc=report_file_path)
        db.session.add(report)
        db.session.commit()
        writ.check_status = 'finished'
        if province != '':
            writ.province = province
        if writ_date != '':
            writ.writ_date = writ_date
        db.session.commit()
        return
