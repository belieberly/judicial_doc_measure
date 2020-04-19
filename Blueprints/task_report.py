import _thread

from flask import Blueprint, send_file, request, g, abort

from auth import auth
from database.models import AnalysisReport, User
import json


blueprint_task_report = Blueprint('task_report', __name__)


@blueprint_task_report.route('/<task_id>', methods=['GET'])
@auth.login_required
def get_task_report(task_id):
    user_id = g.user['open_id']
    user = User.query.get(user_id)
    if user.tasks.filter_by(id=task_id).first():
        report = AnalysisReport.query.filter_by(task_id=task_id).first()
        report_file = open(report.loc, 'r', encoding='utf-8')
        report_json = json.load(report_file)
        return report_json
    abort(403)



@blueprint_task_report.route('/<task_id>/json',methods = ['GET'])
@auth.login_required
def get_task_report_json(task_id):
    user_id = g.user['open_id']
    user = User.query.get(user_id)
    if user.tasks.filter_by(id=task_id).first():
        analysis_report = AnalysisReport.query.filter_by(task_id=task_id).first()
        return send_file(analysis_report.loc)
    abort(403)

