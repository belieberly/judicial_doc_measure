# from flasgger import swag_from
import time
import uuid

from flask import Blueprint, request, jsonify, g
from sqlalchemy import and_

from database.models import db, User, JudicialDoc, Task
import config as cf
import json
import web_utils
from auth import auth
import _thread

from my_celery_client import my_celery_app

blueprint_task = Blueprint('task', __name__)


# 上传单个zip文件或多个xml文件
# 返回字符串格式，文件名称用逗号隔开
@blueprint_task.route('', methods=['POST', 'GET'])
@auth.login_required
def build_task():
    def post():
        user_id = g.user['open_id']
        user = User.query.get(user_id)
        request_dic = request.json
        task_name = request_dic['title']
        writ_id_list = request_dic['writs']
        tmp_task_uuid = str(uuid.uuid4())
        upload_time = time.time()
        upload_time = web_utils.timestamp2time(upload_time)
        task = Task(id=tmp_task_uuid, user_id=g.user['open_id'], name=task_name, date=upload_time,
                    length=len(writ_id_list), progress_status='waiting')
        db.session.add(task)
        db.session.commit()
        if 'useDefault' in request_dic.keys() and request_dic['useDefault'] == True:
            input_index_dic = json.loads(user.config.first().config_json)
            print(input_index_dic)
        else:
            input_index_dic = request_dic['config']
        try:
            my_celery_app.send_task('task_measure_thread',
                                    args=[writ_id_list, input_index_dic, task_name, tmp_task_uuid, upload_time])
        except Exception as e:
            print(e)
            print('创建任务进程失败')
        return '在创建啦'

    def get():
        user_id = g.user['open_id']
        task_list = []
        condition = (Task.user_id == user_id)
        if request.values.get('name'):
            condition = and_(condition, Task.docname.like('%' + request.values.get('name') + '%'))
        if request.values.get('startTime'):
            start_timestamp = request.values.get('startTime')
            start_time = web_utils.timestamp2time(int(start_timestamp) / 1000)
            condition = and_(condition, Task.date > start_time)
        if request.values.get('endTime'):
            end_timestamp = request.values.get('endTime')
            end_time = web_utils.timestamp2time(int(end_timestamp) / 1000)
            condition = and_(condition, Task.date < end_time)
        if request.values.get('status'):
            status = request.values.get('status')
            condition = and_(condition, Task.progress_status == status)
        tasks_operator = Task.query.filter(condition)
        if request.values.get('pageIndex'):
            page_index = int(request.values.get('pageIndex'))
        else:
            page_index = 1
        if request.values.get('pageSize'):
            page_size = int(request.values.get('pageSize'))
        else:
            page_size = None
        total_len = tasks_operator.count()
        tasks = tasks_operator.paginate(page=page_index, per_page=page_size).items
        for task in tasks:
            task_tmp = {'id': task.id, 'title': task.name, 'time': web_utils.time2timestamp(task.date) * 1000,
                        'status': task.progress_status, 'length': task.length}
            task_list.append(task_tmp)
        res = {'result': task_list, 'total': total_len}
        return jsonify(res)

    if request.method == 'POST':
        return post()
    else:
        return get()


@blueprint_task.route('/<task_id>/status', methods=['GET'])
@auth.login_required
def get_task_status(task_id):
    task = Task.query.filter_by(id=task_id).first()
    return task.progress_status
