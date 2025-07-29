import numpy as np

def block_circulant(blocks):
    r, c = blocks[0].shape
    B = np.zeros((len(blocks) * r, len(blocks) * c), dtype=blocks[0].dtype)
    for k in range(len(blocks)):
        for l in range(len(blocks)):
            kl = np.mod(k + l, len(blocks))
            B[r * kl : r * (kl + 1), c * k : c * (k + 1)] = blocks[l]
    return B

def random_corr_matrix(p, mean_corr):
    corr = np.full((p, p), mean_corr)
    noise = np.random.normal(scale=0.1, size=(p, p))
    np.fill_diagonal(noise, 0)
    corr += noise
    np.fill_diagonal(corr, 1)
    corr = (corr + corr.T) / 2  # make sure its symmetric
    return np.clip(corr, 0, 1)
