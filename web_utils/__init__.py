import datetime
import time
from dateutil import tz
import config as cf


# def write_intersect_properties(input_dict, target_dict):
#     # input_dict网络传来的properties, target_dict数据库读出来的properties
#     # 返回写好的properties
#     input_set = set(input_dict.keys())
#     target_set = set(target_dict.keys())
#     inter_set = input_set & target_set
#     for key in inter_set:
#         target_dict[key] = input_dict[key]
#     return target_dict


# 返回需要度量的指标
def get_index(input_dic):
    subject_index = cf.subject_index
    object_index = cf.object_index
    subject_list = []
    object_list = []
    index_list = []
    for i in input_dic:
        if i in subject_index.keys() and input_dic[i] == 1:
            subject_list.append(i)
            index_list.append(i)
        elif i in object_index.keys() and input_dic[i] == 1:
            object_list.append(i)
            index_list.append(i)
    return subject_list, object_list, index_list


def get_userid():
    return 1


def timestamp2time(now_time):
    now = datetime.datetime.fromtimestamp(now_time)  # 时间戳转datetime
    return now


def time2timestamp(now):
    now_time = int(time.mktime(now.timetuple()))  # datetime 转时间戳
    # utc_naive = now.replace(tzinfo=None) - now.utcoffset()
    # print(utc_naive)
    # now_time = (utc_naive-datetime.datetime(1970, 1, 1)).total_seconds()
    return now_time

# now = datetime.datetime.now()
# print(now)
# stamp = time2timestamp(now)
# print(stamp)
# test = timestamp2time(stamp)
# print(test)
