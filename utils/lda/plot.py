import pandas as pd
from gensim import corpora, models
from gensim.corpora.mmcorpus import MmCorpus
import re

import matplotlib.pyplot as plt

T = []
power = []
# dict = [[10, 173.91674517622565], [20, 160.26221955907317], [30, 153.76570760784446], [40, 149.24843122796773],
#         [50, 142.69966133866714], [60, 139.57748478636228], [70, 136.86572479427863], [80, 149.32669681394538],
#         [90, 190.5626319110085], [100, 183.5612814112729], [110, 179.88624326798686], [120, 177.9183091636943],
#         [130, 174.02463721456562], [140, 170.99793851795746]]
# 10,150,10
dict1 = [[10, 32.62238586953784], [20, 31.712570172068794], [30, 31.370462018959426], [40, 31.660234685161598],
         [50, 31.940929804062886], [60, 31.51449692287337], [70, 34.550360281003734], [80, 37.95461939719253],
         [90, 49.49517290676269], [100, 70.32023734073742], [110, 109.02426347529286], [120, 151.84857721104962],
         [130, 116.09998623368561], [140, 116.09998851463087]]

dict2 = [[20, 26.320172986694455], [23, 26.445982502975898], [26, 26.21010249451223], [29, 26.124010574247322], [32, 26.24364024174366], [35, 26.176837617717993], [38, 25.978321065361033], [41, 26.911748956211405], [44, 26.356475476970243], [47, 26.100506296425202], [50, 26.343413303064377], [53, 26.84379893314494], [56, 26.86801503905892], [59, 26.828447712600507]]


for i in dict2:
    T.append(i[0])
    power.append(i[1])
plt.plot(T, power)
plt.xlabel('Num of Topic')
plt.ylabel('Perplexity')
plt.show()
plt.savefig('./perplexity.png')

# data = pd.read_csv("./cail_0518/process.csv", encoding="utf-8", header=None)
# corpus = MmCorpus('./cail_0518/corpora.mm')
# data[2] = data[1].apply(lambda x: re.split(r'\s*', x))
#
# corpora_documents = []
#
# for item_str in data[2]:
#     corpora_documents.append(item_str)
# del corpora_documents[0]
#
# dict_1 = corpora.Dictionary(corpora_documents)
#
# dict_corpora = [dict_1.doc2bow(i) for i in corpora_documents]
#
# tfidf = models.TfidfModel(dict_corpora)
# corpus_tfidf = tfidf[dict_corpora]
#
# print(dict_corpora)
