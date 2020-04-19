import pandas as pd
import numpy as np
from gensim import corpora, models
import re
import logging
import math

SOME_FIXED_SEED = 20

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
data = pd.read_csv("./lda_model/process.csv", encoding="utf-8", header=None)

data[2] = data[1].apply(lambda x: re.split(r'\s*', x))

corpora_documents = []
# print(data[2])
for item_str in data[2]:
    # print(item_str)
    corpora_documents.append(item_str)
del corpora_documents[0]

dict_1 = corpora.Dictionary(corpora_documents)
# dict_1.save('./cail_0518/dict_v2')
dict_corpora = [dict_1.doc2bow(i) for i in corpora_documents]

# 向量的每一个元素代表了一个word在这篇文档中出现的次数
# print(corpus)
from gensim.corpora.mmcorpus import MmCorpus
# MmCorpus.serialize('ths_corpora.mm', dict_corpora)  # 将生成的语料保存成MM文件


# #
tfidf = models.TfidfModel(dict_corpora)
corpus_tfidf = tfidf[dict_corpora]

np.random.seed(SOME_FIXED_SEED)

def perplexity(ldamodel, testset, dictionary, size_dictionary, num_topics):
    """calculate the perplexity of a lda-model"""
    # dictionary : {7822:'deferment', 1841:'circuitry',19202:'fabianism'...]
    print('the info of this ldamodel: \n')
    print('num of testset: %s; size_dictionary: %s; num of topics: %s' % (len(testset), size_dictionary, num_topics))
    prep = 0.0
    prob_doc_sum = 0.0
    topic_word_list = []  # store the probablity of topic-word:[(u'business', 0.010020942661849608),(u'family', 0.0088027946271537413)...]
    for topic_id in range(num_topics):
        topic_word = ldamodel.show_topic(topic_id, size_dictionary)
        dic = {}
        for word, probability in topic_word:
            dic[word] = probability
        topic_word_list.append(dic)
    doc_topics_ist = []  # store the doc-topic tuples:[(0, 0.0006211180124223594),(1, 0.0006211180124223594),...]
    for doc in testset:
        doc_topics_ist.append(ldamodel.get_document_topics(doc, minimum_probability=0))
    testset_word_num = 0
    for i in range(len(testset)):
        prob_doc = 0.0  # the probablity of the doc
        doc = testset[i]
        doc_word_num = 0  # the num of words in the doc
        for word_id, num in doc:
            prob_word = 0.0  # the probablity of the word
            doc_word_num += num
            word = dictionary[word_id]
            for topic_id in range(num_topics):
                # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                prob_topic = doc_topics_ist[i][topic_id][1]
                prob_topic_word = topic_word_list[topic_id][word]
                prob_word += prob_topic * prob_topic_word
            prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
        prob_doc_sum += prob_doc
        testset_word_num += doc_word_num
    prep = math.exp(-prob_doc_sum / testset_word_num)  # perplexity = exp(-sum(p(d)/sum(Nd))
    #print("the perplexity of this ldamodel is : %s" % prep)
    return prep

topicnum_perplexity = []
corpus = MmCorpus('./ths_corpora.mm')
testset = []
import random
for i in random.sample(range(corpus.num_docs), corpus.num_docs//100):
    testset.append(corpus[i])

for topic_num in range(20, 60, 3):
    # lda = models.LdaModel(dict_corpora, num_topics=topic_num, id2word=dict_1, iterations=1000)
    # prep = perplexity(lda, testset, dict_1, len(dict_1.keys()), topic_num)
    # print(topic_num, "success!!!!!!!!!!!!!!!!!!!", prep)
    # topicnum_perplexity.append([topic_num, prep])

    lda_tfidf = models.LdaModel(corpus_tfidf, num_topics=topic_num, id2word=dict_1, iterations=1000)
    prep = perplexity(lda_tfidf, testset, dict_1, len(dict_1.keys()), topic_num)
    print(topic_num, "success tfidf!!!!!!!!!!!!!!!!!!!", prep)
    topicnum_perplexity.append([topic_num, prep])
print(topicnum_perplexity)
