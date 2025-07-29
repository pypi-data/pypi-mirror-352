import gc
import itertools
import math
import time
import numpy as np
import jax
import jax.numpy as jnp
from ott.geometry import geometry
from ott.problems.linear import linear_problem
from ott.solvers.linear import sinkhorn
from sklearn.cluster import KMeans
import ot

@jax.jit
def get_wrd(w1, w2):
    w1_norm = jnp.linalg.norm(w1, axis=1)
    m1 = w1_norm / w1_norm.sum()

    w2_norm = jnp.linalg.norm(w2, axis=1)
    m2 = w2_norm / w2_norm.sum()

    w_dot = jnp.dot(w1, w2.T)
    w_norm = jnp.outer(w1_norm, w2_norm.T)
    c = 1 - w_dot / w_norm

    geom = geometry.Geometry(cost_matrix=c)

    prob = linear_problem.LinearProblem(geom, m1, m2)
    solver = sinkhorn.Sinkhorn(threshold=0.001, max_iterations=2000)
    out = solver(prob)

    return out.reg_ot_cost

class SubspaceWRD:
    def __init__(self, max_iter=1000, division_size=2000):
        self.max_iter = max_iter
        self.division_size = division_size

    def stable_softmax(self, x):
        shiftx = x - np.max(x)
        exps = np.exp(shiftx)

        return exps / np.sum(exps)

    def init_base_vecs(self, s_vecs, k):
        all_w_vecs = list(itertools.chain.from_iterable(s_vecs))

        kmeans = KMeans(n_clusters=k)
        kmeans.fit(all_w_vecs)

        W = kmeans.cluster_centers_

        b = np.ones(k) / k

        return W, b

    def get_fixed_s_vec(self, X):
        a = np.ones(X.shape[0]) / X.shape[0]

        c = ot.dist(X, self.W, metric='euclidean') ** 2

        t = ot.emd(a, self.b, c)

        return t.T @ X

    def evaluate_pairwise_distance(self, combinations):
        print("Batch {}/{} Start".format(self.batch_number, self.batches))
        self.batch_number += 1

        max_length = max(
            len(self.s_vecs[combinations[-1][0]]),
            len(self.s_vecs[combinations[-1][1]])
        )
        k = math.ceil(max_length * 1.5)

        keys = set(np.concatenate([combinations[:, 0], combinations[:, 1]]).tolist())
        values = [self.s_vecs[key] for key in keys]

        self.W, self.b = self.init_base_vecs(values, k)

        values = list(map(self.get_fixed_s_vec, values))

        fixed_s_vecs = dict(zip(keys, values))

        del keys, values
        gc.collect()

        w1s = np.array([np.array(fixed_s_vecs[i]) for i in combinations[:, 0]])
        w2s = np.array([np.array(fixed_s_vecs[j]) for j in combinations[:, 1]])

        del fixed_s_vecs
        gc.collect()

        w1s_size = w1s.shape[0] * w1s.shape[1] * w1s.shape[2] * 128 / 8
        w2s_size = w2s.shape[0] * w2s.shape[1] * w2s.shape[2] * 128 / 8

        print(w1s.shape)
        print(w2s.shape)
        print( 'Estimate Memory Usage: {:.2f}MB'.format(((w1s_size + w2s_size) / 1024 /1024)))

        start = time.perf_counter()
        batched_wrd = jax.vmap(get_wrd, in_axes=(0, 0))
        result = batched_wrd(w1s, w2s)
        end = time.perf_counter()

        del w1s, w2s
        gc.collect()

        print('Batch Done with {:.2f}sec'.format((end-start)))
        return result

    def run(self, s_vecs, combinations=None):
        self.s_vecs = s_vecs

        if combinations is None:
            combinations = list(itertools.combinations(range(len(s_vecs)), 2))
        else:
            combinations = combinations
        combinations = np.array(combinations)

        lengths = np.array([max(len(s_vecs[i]), len(s_vecs[j])) for i, j in combinations])

        combinations = combinations[np.argsort(lengths)]
        lengths = np.sort(lengths)

        vec_size = 128 / 8 * 200

        splitted_combinations = []
        i = len(combinations)
        for j in reversed(range(len(combinations))):
            k = math.ceil(lengths[i - 1] * 1.5)
            if (i - j) * k * vec_size * 2 > (self.division_size * 1024 * 1024):
                splitted_combinations.append(combinations[j+1:i])
                i = j + 1

        if i != 0:
            splitted_combinations.append(combinations[0:i])

        splitted_combinations = splitted_combinations[::-1]
        self.batches = len(splitted_combinations)
        self.batch_number = 1

        distances = list(map(self.evaluate_pairwise_distance, splitted_combinations))
        distances = np.concatenate(distances)

        return combinations[np.argsort(distances)], np.sort(distances)