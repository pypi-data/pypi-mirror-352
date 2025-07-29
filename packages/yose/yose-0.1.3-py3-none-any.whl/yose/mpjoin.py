import hashlib
from collections import defaultdict

class MPJoin:
    def __init__(self, min_cos_sim=0.70, hash_func=hashlib.md5, hashbits=64):
        self.max_distance = int(64 * (1 - min_cos_sim))
        self.hash_func = hash_func
        self.hashbits = hashbits

    def hash_feature(self, feature, hashbits=64):
        h = int(self.hash_func(feature.encode('utf-8')).hexdigest(), 16)
        return [(h >> i) & 1 for i in range(hashbits)]

    def simhash(self, tokens):
        v = [0] * self.hashbits
        for token in tokens:
            h = self.hash_feature(token, self.hashbits)
            for i in range(self.hashbits):
                v[i] += 1 if h[i] else -1
        bit_list = [1 if bit > 0 else 0 for bit in v]
        return sum([bit << i for i, bit in enumerate(bit_list)])

    def hamming_distance(self, x, y):
        return bin(x ^ y).count('1')

    def mpjoin_simhash(self, hashes):
        bands = self.max_distance + 1
        band_size = self.hashbits // bands

        inverted_index = [defaultdict(set) for _ in range(bands)]

        result = set()
        for idx, h in enumerate(hashes):
            for b in range(bands):
                band_mask = ((1 << band_size) - 1) << (b * band_size)
                band_value = (h & band_mask) >> (b * band_size)
                inverted_index[b][band_value].add(idx)

        seen = set()
        for b in range(bands):
            for idx_list in inverted_index[b].values():
                idx_list = list(idx_list)
                for i in range(len(idx_list)):
                    for j in range(i + 1, len(idx_list)):
                        a, b = idx_list[i], idx_list[j]
                        if (a, b) not in seen and (b, a) not in seen:
                            seen.add((a, b))
                            if self.hamming_distance(hashes[a], hashes[b]) <= self.max_distance:
                                result.add((a, b))

        return result

    def run(self, tokenized_s):
        hashes = list(map(self.simhash, tokenized_s))
        return list(self.mpjoin_simhash(hashes))