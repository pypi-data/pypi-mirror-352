import numpy as np

class Word2Vec:
    def __init__(self, kv):
        self.kv = kv

    def get_w_vecs(self, tokens):
        return np.array([np.array(self.kv[token]) for token in tokens if token in self.kv])

    def run(self, tokenized_s):
        return list(map(self.get_w_vecs, tokenized_s))