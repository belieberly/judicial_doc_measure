import datetime
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from database.models import db, User, JudicialDoc, Report
import config as cf
import zipfile
import uuid
import json
import web_utils
from my_celery.with_flask_context_task import doc_measure_thread
from my_celery.with_flask_context_task import flask_app_context

blueprint_writ = Blueprint('writ', __name__)


# 上传单个zip文件或多个xml文件
# 返回字符串格式，文件名称用逗号隔开
@blueprint_writ.route('/upload', methods=['POST'])
@swag_from('../api_description/upload.yml')
def upload_file():
    # db.drop_all()
    db.create_all()
    user = User(username='01', password='123456')
    db.session.add(user)
    db.session.commit()
    basepath = cf.upload_base_dir
    file_list = request.files.getlist('file')
    # upload_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    upload_time = datetime.datetime.now()
    res = []
    if len(file_list) == 0:
        print('no file upload')
        return ','.join(res)
    elif len(file_list) == 1:
        print('上传一个文件')
        file_type = file_list[0].filename.split('.')[-1]
        if file_type == 'zip':
            zf = zipfile.ZipFile(file_list[0])
            print(zf.namelist())
            for name in zf.namelist():
                if name.split('.')[-1] != 'xml':
                    continue
                else:
                    tmp_uuid = str(uuid.uuid4())
                    upload_path = basepath + tmp_uuid + name.split('/')[-1]
                    print(upload_path)
                    hFile = open(upload_path, 'wb')
                    hFile.write(zf.read(name))
                    hFile.close()
                    doc = JudicialDoc(id=tmp_uuid, user_id=web_utils.get_userid(), docname=name, date=upload_time,
                                      check_status='untested', length=0, loc=upload_path)
                    db.session.add(doc)
                    db.session.commit()
                    res.append(name)
            return json.dumps(res)
        elif file_type == 'xml':
            print('文件类型为xml')
            tmp_uuid = str(uuid.uuid4())
            name = file_list[0].filename
            # upload_path = os.path.join(basepath,filename)
            upload_path = basepath + tmp_uuid + '_' + name
            file_list[0].save(upload_path)
            print('保存成功')
            doc = JudicialDoc(id=tmp_uuid, user_id=web_utils.get_userid(), docname=name, date=upload_time,
                              check_status='untested', length=0, loc=upload_path)
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
                doc = JudicialDoc(id=tmp_uuid, user_id=web_utils.get_userid(), docname=name, date=upload_time,
                                  check_status='untested', length=0, loc=upload_path)
                db.session.add(doc)
                db.session.commit()
                res.append(name)
        return json.dumps(res)


# # get取配置项 post写配置项
# @blueprint_writ.route('/config', methods=['GET', 'POST'])
# def set_config():
#     if request.method == 'GET':
#         user_id = web_util.get_userid()
#         User.query.filter_by(id=user_id).first()
#         request.get_json()
#     return


@blueprint_writ.route('/writ_list', methods=['GET'])
@swag_from('../api_description/get_list.yml')
def get_writ_list():
    # db.drop_all()
    # db.create_all()
    # user = User(username='01', password='123456')
    # db.session.add(user)
    # db.session.commit()
    user_id = web_utils.get_userid()
    print(user_id)
    user = User.query.get(user_id)
    # print(user)
    doc_list = []
    if request.values.get('name'):
        docs = user.docs.filter(JudicialDoc.docname.like('%' + request.values.get('name') + '%'))
        # print(docs)
    if request.values.get('startTime'):
        print('开始时间')
        start_timestamp = request.values.get('startTime')
        print('获取时间戳：', start_timestamp)
        start_time = web_utils.timestamp2time(int(start_timestamp))
        print(start_time)
        docs = docs.filter(JudicialDoc.date > start_time)
    if request.values.get('endTime'):
        print('结束时间')
        end_timestamp = request.values.get('endTime')
        print('获取时间戳：', end_timestamp)
        end_time = web_utils.timestamp2time(int(end_timestamp))
        print(end_time)
        docs = docs.filter(JudicialDoc.date < end_time)
    if not (request.values.get('name') or request.values.get('startTime') or request.values.get('endTime')):
        docs = user.docs.all()
        # print(docs)
    for doc in docs:
        doc_tmp = {'id': doc.id, 'name': doc.docname, 'time': doc.date, 'length': doc.length,
                   'status': doc.check_status}
        doc_list.append(doc_tmp)
    return jsonify({'doc_list': doc_list})


# @blueprint_writ.route('./writ_report/<writ_id>',methods = ['GET'])
@blueprint_writ.route('/writ_report', methods=['GET'])
# @swag_from('../api_description/get_writ_report.yml')
def get_writ_report():
    writ_id = request.values.get('writ-id')
    print(writ_id)
    report = Report.query.filter_by(doc_id=writ_id).first()
    report_file = open(report.loc, 'r', encoding='utf-8')
    report_json = json.load(report_file)
    return report_json


@blueprint_writ.route('/doc_measure', methods=['GET'])
@swag_from('../api_description/get_writ_report.yml')
def doc_measure():
    writ_id = request.values.get('writ-id')
    print(writ_id)
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
        # _thread.start_new_thread(doc_measure_thread,(writ_id,input_index_dic))
        print('celery啥时候调度啊')
        # doc_measure_thread.delay(writ_id, input_index_dic)
        flask_app_context.delay()
    except:
        print('无法启动线程')
    return '后端开始检测'
