import numpy as np
from utils.SVC.preprocession import processing_word, get_stop_words
from utils.SVC.comment_analysis import build_word_vector
from gensim.models.word2vec import Word2Vec
import joblib


# 载入word2vec和svm训练好的模型做预测
def svm_predict(comment):
    n_dim = 300
    svm_model = joblib.load('E:/pycharm/judicial_doc_measurement/utils/SVC/svm_model.pkl')
    w2v_model = Word2Vec.load('E:/pycharm/judicial_doc_measurement/utils/SVC/w2v_model.pkl')
    stop_words_list = get_stop_words()
    processed_comment = processing_word(comment, stop_words_list)
    comment_row = np.array(processed_comment).reshape(1, -1)
    comment_vectors = np.concatenate([build_word_vector(z, n_dim, w2v_model) for z in comment_row])

    predict_result = svm_model.predict(comment_vectors)
    probs = svm_model.predict_proba(comment_vectors)
    # 几位小数
    h = round(probs[0][1], 2)
    c = round(probs[0][0], 2)

    # if int(predict_result) == 0:
    #     print('差评')
    #     #return "0"
    # else:
    #     print('好评')
    #     #return "1"
    # print('置信度为：好评', h, '差评', c)
    return h, c


def svm_predict1(comment):
    n_dim = 300
    svm_model = joblib.load('E:/pycharm/judicial_doc_measurement/utils/SVC/svm1_model.pkl')
    w2v_model = Word2Vec.load('E:/pycharm/judicial_doc_measurement/utils/SVC/w2v1_model.pkl')
    stop_words_list = get_stop_words()
    processed_comment = processing_word(comment, stop_words_list)
    comment_row = np.array(processed_comment).reshape(1, -1)
    comment_vectors = np.concatenate([build_word_vector(z, n_dim, w2v_model) for z in comment_row])

    predict_result = svm_model.predict(comment_vectors)
    probs = svm_model.predict_proba(comment_vectors)
    # 几位小数
    h = round(probs[0][1], 2)
    c = round(probs[0][0], 2)

    # if int(predict_result) == 0:
    #     print('差评')
    #     #return "0"
    # else:
    #     print('好评')
    #     #return "1"
    # print('置信度为：好评', h, '差评', c)
    return h, c

# svm_predict("我讨厌写代码")


# strs = []
# for i in range(1000):
#     with open("D:/2000/pos/pos."+ str(i) +".txt", 'rt', encoding='utf-8') as f:  # 打开文件
#         data = f.read()  # 读取文件
#         strs.append(data.strip())
#         print(str(i) + strs[i])
# starttime = datetime.datetime.now()
# a = 0
# for i in strs:
#     a = a + int(svm_predict(i))
#     print(a)
# endtime = datetime.datetime.now()
# print (endtime - starttime).seconds
# print("   ")
# print("jkhk"+a)
