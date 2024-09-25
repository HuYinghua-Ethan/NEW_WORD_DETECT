import math
from collections import defaultdict


"""
load_corpus()
word_count 统计每个词出现的次数
left_neighbor_entropy 统计每个词左邻的熵
right_neighbor_entropy 统计每个词右邻的熵

calc_pmi() : log P(W) / (P(c1) * P(c2) ... * P(cn)) / n
word_count_by_length 统计 ngram 的词总数
统计词出现的频率
然后统计词中每个字出现的频率
然后根据公式 log P(W) / (P(c1) * P(c2) ... * P(cn)) / n 计算出互信息

calc_entropy() : 计算熵
- sum(Pi * logPi)

calc_word_values：
pmi * min(le, re)  值越大，作为一个词的可能性就越大

"""

class NewWordDetect:
    def __init__(self, corpus_path):
        self.max_word_length = 5  # 词的最大长度为5
        self.word_count = defaultdict(int)  # 词频
        self.left_neighbor_entropy = defaultdict(dict)  # 左邻熵
        self.right_neighbor_entropy = defaultdict(dict)  # 右邻熵
        self.load_corpus(corpus_path)
        self.calc_pmi()
        self.calc_entropy()
        self.calc_word_values()

    # 加载语料数据，并进行统计
    def load_corpus(self, path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                sentence = line.strip()
                for word_length in range(1, self.max_word_length):
                    self.ngram_count(sentence, word_length)
        return

    # 记录窗口的长度，记录左邻和右邻
    def ngram_count(self, sentence, word_length):
        for i in range(len(sentence) - word_length + 1):
            word = sentence[i:i + word_length]
            self.word_count[word] += 1
            if i - 1 >= 0:
                char = sentence[i - 1]
                self.left_neighbor_entropy[word][char] = self.left_neighbor_entropy[word].get(word, 0) + 1
            if i + word_length < len(sentence):
                char = sentence[i + word_length]
                self.right_neighbor_entropy[word][char] = self.right_neighbor_entropy[word].get(word, 0) + 1
        return
    
    # 统计 ngram 的词总数
    def calc_total_count_by_length(self):
        self.word_count_by_length = defaultdict(int)
        for word, count in self.word_count.items():
            self.word_count_by_length[len(word)] += count
        return

     # 计算互信息(pointwise mutual information)  log P(W) / (P(c1) * P(c2) ... * P(cn)) / n
    def calc_pmi(self):
        self.calc_total_count_by_length()
        self.pmi = {}
        for word, count in self.word_count.items():
            p_word = count / self.word_count_by_length[len(word)]
            p_chars = 1
            for char in word:
                p_chars *= self.word_count[char] / self.word_count_by_length[1]
            self.pmi[word] = math.log(p_word / p_chars, 10) / len(word)
        return        
    
    # 计算熵 - sum(Pi * logPi)
    def calc_entropy_by_word_count_dict(self, word_count_dict):
        total = sum(word_count_dict.values())
        entropy = sum([-(c / total) * math.log((c / total), 10) for c in word_count_dict.values()])
        return entropy
    
    # 计算左右邻熵
    def calc_entropy(self):
        self.word_left_entropy = {}
        self.word_right_entropy = {}
        for word, count_dict in self.left_neighbor_entropy.items():
            self.word_left_entropy[word] = self.calc_entropy_by_word_count_dict(count_dict)
        for word, count_dict in self.right_neighbor_entropy.items():
            self.word_right_entropy[word] = self.calc_entropy_by_word_count_dict(count_dict)    
    
    def calc_word_values(self):
        self.word_values = {}
        for word in self.pmi:
            if len(word) < 2 or "，" in word:
                continue
            pmi = self.pmi.get(word, 1e-3)
            le = self.word_left_entropy.get(word, 1e-3)
            re = self.word_right_entropy.get(word, 1e-3)
            self.word_values[word] = pmi * min(le, re)
        

if __name__ == "__main__":
    nwd = NewWordDetect("sample_corpus.txt")
    value_sort = sorted([(word, count) for word, count in nwd.word_values.items()], key=lambda x: x[1], reverse=True)
    print([x for x, c in value_sort if len(x) == 2][:10])
    print([x for x, c in value_sort if len(x) == 3][:10])
    print([x for x, c in value_sort if len(x) == 4][:10])

