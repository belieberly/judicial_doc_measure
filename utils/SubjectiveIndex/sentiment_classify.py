#
import json
import re

import requests
#
from utils.SVC.comment_predict import svm_predict,svm_predict1
def get_sentiment_result(text):

    """
    利用情感倾向分析API来获取返回数据
    :param text: 输入文本
    :return response: 返回的响应
    """
    if text == '':
        return ''
    # 请求接口
    url = 'https://aip.baidubce.com/oauth/2.0/token'
    # 需要先获取一个 token
    client_id = 'gzd43E1o9zs5oYSYYGH55GUH'
    client_secret = 'ZM3YKTwVyHODswC8gYMOrto5XGpf44ir'
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(url=url, params=params, headers=headers).json()
#
    access_token = response['access_token']
     # 通用版情绪识别接口
    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify'
    # 定制版情绪识别接口
    # url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify_custom'
    # 使用 token 调用情感倾向分析接口
    params = {
        'access_token': access_token
    }
    payload = json.dumps({
        'text': text
    })
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.post(url=url, params=params, data=payload, headers=headers).json()
    return response

def sentiment_index(str):
    pattern = r'，|。|；|：'
    sentence_list1 = re.split(pattern, str)
    sentiment_res = []
    sentiment_score = 0
    for sentence in sentence_list1:
        # res = get_sentiment_result(sentence)['items'][0]
        # positive_porb = res['positive_prob']
        # # negative_prob = res['negative_prob']
        # confidence = res['confidence']
        if len(sentence.strip())!=0:
            positive_porb,negative_prob= svm_predict(sentence)

            # sentence_score = abs(positive_porb-negative_prob)*confidence
            sentiment_res.append((sentence,abs(positive_porb-0.5)))
    return sentiment_res

def sentiment_index1(str):
    pattern = r'(，|。|；|：)'
    sentence_list1 = re.split(pattern, str)
    sentiment_res = []
    sentiment_score = 0
    for sentence in sentence_list1:
        # res = get_sentiment_result(sentence)['items'][0]
        # positive_porb = res['positive_prob']
        # # negative_prob = res['negative_prob']
        # confidence = res['confidence']
        if len(sentence.strip())!=0:
            positive_porb,negative_prob= svm_predict1(sentence)

            # sentence_score = abs(positive_porb-negative_prob)*confidence
            sentiment_res.append((sentence,abs(positive_porb-0.5)))
    return sentiment_res



if __name__ == '__main__':
    # print(get_sentiment_result('本院认为嫌疑人罪孽深重'))
    #
    # print(get_sentiment_result('被告有醉酒作案嫌疑'))
    str1 = '黑粉是黑暗的代表'
    res = get_sentiment_result(str1)['items'][0]
    positive_porb = res['positive_prob']
    # negative_prob = res['negative_prob']
    confidence = res['confidence']
    print(res)


