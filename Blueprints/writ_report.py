import json
from auth import auth
from flask import Blueprint, request, jsonify, g
from database.models import db, User, JudicialDoc, Report, Config
from my_celery_client import my_celery_app

blueprint_writ_report = Blueprint('writ_report', __name__)




@blueprint_writ_report.route('', methods=['POST'])
# @swag_from('../api_description/get_writ_report.yml')
@auth.login_required
def doc_measure():
    user_id = g.user['open_id']
    user = User.query.get(user_id)
    request_dic = request.json
    if 'useDefault' in request_dic.keys() and request_dic['useDefault']==True:
        input_index_dic = json.loads(user.config.first().config_json)
        print(input_index_dic)
    else:
        input_index_dic = request_dic['config']
    writ_id = request_dic['writId']
    writ = JudicialDoc.query.get(writ_id)
    writ.check_status = 'waiting'
    db.session.commit()
    try:
        # _thread.start_new_thread(doc_measure_thread,(writ_id,input_index_dic))
        print('celery啥时候调度啊')
        my_celery_app.send_task('doc_measure_thread', args=[writ_id, input_index_dic])
    except:
        print('无法启动线程')
    return '后端开始检测'




@blueprint_writ_report.route('/<writ_id>', methods=['GET'])
@auth.login_required
# @swag_from('../api_description/get_writ_report.yml')
def get_writ_report(writ_id):
    report = Report.query.filter_by(doc_id=writ_id).first()
    report_file = open(report.loc, 'r', encoding='utf-8')
    report_json = json.load(report_file)
    return report_json