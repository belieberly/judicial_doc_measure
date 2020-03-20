from flasgger import swag_from
from flask import Blueprint, jsonify
from database.models import Config
import json
from config import *
names = locals()

import web_utils

blueprint_my_config = Blueprint('my_config', __name__)

@blueprint_my_config.route('/my_config')
@swag_from('../api_description/get_my_config.yml')
def get_my_config():
    id  = web_utils.get_userid()
    config = Config.query.filter_by(user_id = id).first()
    config_json = json.loads(config.config_json)
    my_config = []
    for index in config_json:
        label = index.strip('_')
        config_item = {"value":index,"label":names['index'][label],"component":"switch","type":"number"}
        my_config.append(config_item)
    return jsonify({'doc_list': my_config})
