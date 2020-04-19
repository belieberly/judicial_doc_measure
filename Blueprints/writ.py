# from flasgger import swag_from
from flask import Blueprint, request, jsonify, g
from database.models import db, User, JudicialDoc
import config as cf
import zipfile
import uuid
import json
import web_utils
from auth import auth
import time
from sqlalchemy.sql import and_, True_

blueprint_writ = Blueprint('writ', __name__)


# 上传单个zip文件或多个xml文件
# 返回字符串格式，文件名称用逗号隔开
@blueprint_writ.route('', methods=['POST', 'GET'])
@auth.login_required
# @cross_origin(origin='http://localhost:5500')
def upload_file():
    def post():
        basepath = cf.upload_base_dir
        file_list = request.files.getlist('file')
        # upload_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        upload_time = time.time()
        upload_time = web_utils.timestamp2time(upload_time)
        res = []
        if len(file_list) == 0:
            print('no file upload')
            return ','.join(res)
        elif len(file_list) == 1:
            print('upload one file successfully')
            file_type = file_list[0].filename.split('.')[-1]
            if file_type == 'zip':
                zf = zipfile.ZipFile(file_list[0])
                # print(zf.namelist())
                for name in zf.namelist():
                    if name.split('.')[-1] != 'xml':
                        continue
                    else:
                        tmp_uuid = str(uuid.uuid4())
                        upload_path = basepath + tmp_uuid + name.split('/')[-1]
                        # print(upload_path)
                        hFile = open(upload_path, 'wb')
                        file_bytes = zf.read(name)
                        file_length = len(file_bytes)
                        hFile.write(file_bytes)
                        hFile.close()
                        doc = JudicialDoc(id=tmp_uuid, user_id=g.user['open_id'], docname=name, date=upload_time,
                                          check_status='untested', length=file_length, loc=upload_path)
                        db.session.add(doc)
                        db.session.commit()
                        res.append(name)
                return json.dumps(res)
            elif file_type == 'xml':
                print('文件类型为xml')
                tmp_uuid = str(uuid.uuid4())
                name = file_list[0].filename
                upload_path = basepath + tmp_uuid + '_' + name
                file2save = open(upload_path, 'wb')
                tmp_file = file_list[0]
                file_bytes = tmp_file.read()
                tmp_length = len(file_bytes)
                file2save.write(file_bytes)
                print('保存成功')
                doc = JudicialDoc(id=tmp_uuid, user_id=g.user['open_id'], docname=name, date=upload_time,
                                  check_status='untested', length=tmp_length, loc=upload_path)
                db.session.add(doc)
                db.session.commit()
                res.append(name)
                return json.dumps(res)
            else:
                return json.dumps(res)
        else:
            for file in file_list:
                name = file.filename
                file_type = name.split('.')[-1]
                if file_type != 'xml':
                    continue
                else:
                    tmp_uuid = str(uuid.uuid4())
                    # upload_path = os.path.join(basepath,filename)
                    upload_path = basepath + tmp_uuid + '_' + name
                    file.save(upload_path)
                    print('保存成功')
                    doc = JudicialDoc(id=tmp_uuid, user_id=g.user['open_id'], docname=name, date=upload_time,
                                      check_status='untested', length=0, loc=upload_path)
                    db.session.add(doc)
                    db.session.commit()
                    res.append(name)
            return json.dumps(res)

    def get():
        user_id = g.user['open_id']
        doc_list = []
        condition = (JudicialDoc.user_id == user_id)
        if request.values.get('taskId'):
            condition = and_(condition, JudicialDoc.task_id == request.values.get('taskId'))
        if request.values.get('name'):
            condition = and_(condition, JudicialDoc.docname.like('%' + request.values.get('name') + '%'))
        if request.values.get('startTime'):
            start_timestamp = request.values.get('startTime')
            start_time = web_utils.timestamp2time(int(start_timestamp) / 1000)
            condition = and_(condition, JudicialDoc.date > start_time)
        if request.values.get('endTime'):
            end_timestamp = request.values.get('endTime')
            end_time = web_utils.timestamp2time(int(end_timestamp) / 1000)
            condition = and_(condition, JudicialDoc.date < end_time)
        if request.values.get('status'):
            status = request.values.get('status')
            condition = and_(condition, JudicialDoc.check_status == status)
        docs_operator = JudicialDoc.query.filter(condition)
        if request.values.get('pageIndex'):
            page_index = int(request.values.get('pageIndex'))
        else:
            page_index = 1
        if request.values.get('pageSize'):
            page_size = int(request.values.get('pageSize'))
        else:
            page_size = None
        total_len = docs_operator.count()
        docs = docs_operator.paginate(page=page_index, per_page=page_size).items
        for doc in docs:
            doc_tmp = {'id': doc.id, 'title': doc.docname, 'time': web_utils.time2timestamp(doc.date) * 1000,
                       'length': doc.length,
                       'status': doc.check_status}
            doc_list.append(doc_tmp)
        res = {'result': doc_list, 'total': total_len}
        return jsonify(res)

    if request.method == 'POST':
        return post()
    else:
        return get()


@blueprint_writ.route('/<writ_id>/status', methods=['GET'])
@auth.login_required
def get_writ_status(writ_id):
    writ = JudicialDoc.query.filter_by(id=writ_id).first()
    return writ.check_status
