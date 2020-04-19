import json
import time

import requests
from flask import Blueprint, request
from database.models import db, User,Config
from auth import token_serializer, expires_time
from config import oauth_config
import config as cf

blueprint_user = Blueprint('user', __name__)


@blueprint_user.route('', methods=['GET'])
def login():
    oauth_code = request.args.get('code')
    oauth_url = oauth_config.oauth_url
    oauth_token_type = oauth_config.oauth_token_type
    oauth_token = oauth_config.oauth_token
    oauth_grant_type = oauth_config.oauth_grant_type
    oauth_redirect_uri = oauth_config.oauth_redirect_uri
    oauth_scope = oauth_config.oauth_scope

    headers = {
        'Authorization': oauth_token_type + ' ' + oauth_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # 是uri不是url
    oauth_data = {
        'code': oauth_code,
        'grant_type': oauth_grant_type,
        'redirect_uri': oauth_redirect_uri,
        'scope': oauth_scope

    }

    oauth_response = requests.post(url=oauth_url, data=oauth_data, headers=headers)
    oauth_message = oauth_response.json()
    print(oauth_message)
    access_token = oauth_message['access_token']

    user_url = oauth_config.user_url

    user_response = requests.get(url=user_url, params={'access_token': access_token}, headers=headers)
    raw_user = user_response.json()
    # print(raw_user)
    username = raw_user['name']
    open_id = raw_user['open_id']

    # 查得到用原来的，否则用新的 记得用first()
    tmp_user = User.query.filter_by(id=open_id).first() or User(id=open_id)
    # 更新慕测提供的用户名
    tmp_user.username = username

    config_path = open(cf.transfer_config_path, 'r', encoding='utf-8')
    config_str = json.dumps(json.load(config_path), ensure_ascii=False)
    print(config_str)
    config = Config(user_id=open_id, config_json=config_str)
    print(config)

    db.session.add(tmp_user)
    db.session.add(config)
    db.session.commit()
    user = {'username': username, 'open_id': open_id}

    self_token = token_serializer.dumps(user).decode('utf-8')
    current_millis = round(time.time() * 1000)
    expires_millis = expires_time * 1000

    token_type = oauth_config.token_type

    wrap_user = {
        'selfToken': self_token,
        'username': username,
        'expires': current_millis + expires_millis,
        'tokenType': token_type
    }
    print('token',self_token)

    return wrap_user
