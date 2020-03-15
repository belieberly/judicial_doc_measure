import datetime
import time


def write_intersect_properties(input_dict, target_dict):
    # input_dict网络传来的properties, target_dict数据库读出来的properties
    # 返回写好的properties
    input_set = set(input_dict.keys())
    target_set = set(target_dict.keys())
    inter_set = input_set & target_set
    for key in inter_set:
        target_dict[key] = input_dict[key]
    return target_dict


def is_login(request):
    # 返回是否登录了
    return True


def get_user_id(request):
    # 返回查到的id，这里写数据库唯一的一个用户id
    # 实际可能用header里的token解析，也可能用cookie里的sessionid解析，其中使用cookie提取sessionid在跨域时需要设置CORS
    return '001'


def get_userid():
    return 1


def timestamp2time(now_time):
    now = datetime.datetime.fromtimestamp(now_time)  # 时间戳转datetime
    return now


def time2timestamp(now):
    now_time = int(time.mktime(now.timetuple()))  # datetime 转时间戳
    return now_time
