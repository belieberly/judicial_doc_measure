from flasgger import swag_from
from flask import Blueprint, jsonify, g, request

from auth import auth
from database.models import Config, db
import json
from config import *

names = locals()

import web_utils

blueprint_my_config = Blueprint('my_config', __name__)


@blueprint_my_config.route('', methods=['PUT', 'GET'])
# @swag_from('../api_description/get_my_config.yml')
@auth.login_required
def default_config():
    def get_my_config():
        id = g.user['open_id']
        config = Config.query.filter_by(user_id=id).first()
        config_json = json.loads(config.config_json)
        my_config = []
        for index in config_json:
            label = index.strip('_')
            config_item = {"value": index, "label": names['index'][label], "component": "switch", "type": "number",
                           "result": config_json[index]}
            my_config.append(config_item)
        print(my_config)
        return jsonify(my_config)

    def set_my_config():
        config_dic = request.json
        id = g.user['open_id']
        config = Config.query.filter_by(user_id=id).first()
        config.config_json = json.dumps(config_dic)
        db.session.commit()
        return '成功提交配置项'

    if request.method == 'GET':
        return get_my_config()
    else:
        return set_my_config()
