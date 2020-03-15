# 训练
from gensim.models.word2vec import Word2Vec
from sklearn.preprocessing import StandardScaler
from utils.SVC.preprocession import load_file_and_split
import numpy as np
import joblib
from sklearn import svm


# 获得句子中所有词汇的向量，然后取平均值
def build_word_vector(text, size, comment_w2v):
    vec = np.zeros(size).reshape((1, size))
    count = 0
    for word in text:
        try:
            vec += comment_w2v[word].reshape((1, size))
            count += 1
        except KeyError:
            continue
    if count != 0:
        vec /= count
    return vec


# 训练word2vec模型
def get_train_vecs(x_all_sentences, x_train_sentences, x_test_sentences):
    # 将每个词用300个维度向量化
    n_dim = 300
    # 初始化word2vec模型，默认为cbow模型
    comment_w2v = Word2Vec(size=n_dim, min_count=5)
    # 确定word2vec的词表
    comment_w2v.build_vocab(x_all_sentences)
    # 训练word2vec并模型
    comment_w2v.train(x_all_sentences, total_examples=comment_w2v.corpus_count, epochs=100)
    # 保存模型
    comment_w2v.save('./w2v_model.pkl')
    # 训练数据的向量化
    train_vectors = np.concatenate([build_word_vector(z, n_dim, comment_w2v) for z in x_train_sentences])
    # 测试数据的向量化
    test_vectors = np.concatenate([build_word_vector(z, n_dim, comment_w2v) for z in x_test_sentences])
    # np.save('test_vectors.npy', test_vectors)
    return train_vectors, test_vectors


# 训练svm模型做分类器
def svm_train(train_vecs, y_train, test_vecs, y_test):
    # probability
    clf = svm.SVC(kernel='rbf', verbose=True, probability=True)
    # 均值方差归一化向量
    standardScaler = StandardScaler()
    standardScaler.fit(train_vecs)
    train_vecs = standardScaler.transform(train_vecs)
    test_vecs = standardScaler.transform(test_vecs)
    # 训练svm分类器
    clf.fit(train_vecs, y_train)
    joblib.dump(clf, './svm_model.pkl')
    print(clf.score(test_vecs, y_test))


if __name__ == '__main__':
    x, x_train, x_test, y_train, y_test = load_file_and_split()
    train_vec, test_vec = get_train_vecs(x, x_train, x_test)
    svm_train(train_vec, y_train, test_vec, y_test)
