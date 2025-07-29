import numpy as np

class Screening:
    def __init__(self, std_threshold=2.0):
        self.std_threshold = std_threshold

    def screening_by_vecs(self, s_vecs):
        lengths = np.array([len(w_vecs) for w_vecs in s_vecs])

        nonzero_indices = np.where(lengths > 0)[0]
        valid_indices = np.where(np.abs(lengths - lengths.mean()) < self.std_threshold * lengths.std())[0]
        valid_indices = np.intersect1d(nonzero_indices, valid_indices)

        return valid_indices

    def run(self, sentences, tokenized_s, s_vecs):
          valid_indices = self.screening_by_vecs(s_vecs)

          return [sentences[i] for i in valid_indices], [tokenized_s[i] for i in valid_indices], [s_vecs[i] for i in valid_indices]