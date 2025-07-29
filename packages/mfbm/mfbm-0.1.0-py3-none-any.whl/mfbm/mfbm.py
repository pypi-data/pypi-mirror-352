import numpy as np
from utils import block_circulant

class MFBM:
    def __init__(self, H: np.ndarray, n: int, rho: np.ndarray, eta: np.ndarray, sigma: np.ndarray):
        self.H = H
        self.p = len(self.H)
        self.n = n
        self.m = 1 << (2 * n - 1).bit_length()  # smallest power of 2 greater than 2(n-1)
        self.N = self.m // 2
        self.rho = np.array(rho)
        self.eta = np.array(eta)
        self.sigma = np.array(sigma)
        self.GG = np.block([
            [self.construct_G(np.abs(i - j)) for i in range(1, n + 1)]
            for j in range(1, n + 1)
        ])
        self.circulant_row = self.construct_circulant_row()
        self.C = block_circulant(self.circulant_row)

    def single_cov(self, H: float, h: float):
        assert 0 < H < 1
        assert h >= 0

        H2 = 2 * H
        if h == 0:
            return 1
        return ((h + 1) ** H2 + (h - 1) ** H2 - 2 * (h ** H2)) / 2

    def w_func(self, i: int, j: int, h: float):
        """Exact replica of the formula presented in basic properties of mfbm.
           Not defined for h = 0."""
        if self.H[i] + self.H[j] == 1:
            return self.rho[i, j] * np.abs(h) + self.eta[i, j] * h * np.log(np.abs(h))
        return self.rho[i, j] - self.eta[i, j] * np.sign(h) * np.abs(h) ** (self.H[i] + self.H[j])

    def w(self, i: int, j: int, h: float):
        """Cheaty formula that works"""
        h = abs(h)
        return self.rho[i, j] * h ** (self.H[i] + self.H[j])

    def gamma_func(self, i: int, j: int, h: float):
        return (self.sigma[i] * self.sigma[j]) / 2 * (
            self.w(i, j, h - 1) - 2 * self.w(i, j, h) + self.w(i, j, h + 1)
        )

    def construct_G(self, h: float):
        result = np.ndarray((self.p, self.p))
        for i in range(self.p):
            result[i, i] = self.single_cov(self.H[i], h) * self.sigma[i] ** 2
            for j in range(i):
                result[i, j] = result[j, i] = self.gamma_func(i, j, h)
        return result

    def construct_C(self, j: int):
        if 0 <= j and j < self.m / 2:
            return self.construct_G(j)
        elif j == self.m / 2:
            return (self.construct_G(j) + self.construct_G(j)) / 2
        elif self.m / 2 < j and j <= self.m - 1:
            return self.construct_G(self.m - j)  # basic properties paper says other way around, Wood Chan says this way
        else:
            raise ValueError("argument j must be in the range [0, m-1]")

    def construct_circulant_row(self):
        circulant_row = np.ndarray((self.m, self.p, self.p))  # m number of p x p matrices
        N = self.m // 2
        circulant_row[:N + 1] = [self.construct_G(i) for i in range(N + 1)]
        circulant_row[-N + 1:] = np.flip(circulant_row[1 : N])
        return circulant_row

    def sample_mfgn(self):
        B = np.ndarray((self.m, self.p, self.p), dtype=complex)
        for i in range(self.p):
            for j in range(i + 1):
                B[:, i, j] = np.fft.fft(self.circulant_row[:, i, j])
                if i != j:
                    B[:, j, i] = np.conjugate(B[:, i, j])

        self.transformation = np.ndarray((self.m, self.p, self.p), dtype=complex)
        for i in range(len(self.transformation)):
            e, L = np.linalg.eig(B[i])
            e[e < 0] = 0
            e = np.diag(np.sqrt(e))
            self.transformation[i] = L @ e @ np.conjugate(L.T)

        v1 = np.random.standard_normal((self.p, self.N - 1))
        v2 = np.random.standard_normal((self.p, self.N - 1))
        w = np.ndarray((self.p, 2 * self.N), dtype=complex)
        w[:, 0] = np.random.standard_normal(self.p) / np.sqrt(self.m)
        w[:, self.N] = np.random.standard_normal(self.p) / np.sqrt(self.m)
        w[:, 1 : self.N] = (v1 + 1j*v2) / np.sqrt(4 * self.N)
        w[:, -self.N + 1:] = np.conjugate(w[:, self.N - 1 : 0 : -1])
        w = np.einsum('...ij,j...->i...', self.transformation, w, optimize='optimal')

        ts = np.ndarray((self.p, self.n))
        for i in range(self.p):
            w[i] = np.fft.fft(w[i])
        ts = np.real(w[:, :self.n])
        
        return ts

    def sample(self, T: float = 0) -> np.ndarray:
        if T <= 0:
            T = self.n
        spacing = (T / self.n) ** self.H

        fGns = self.sample_mfgn()[:, :-1]
        ts = np.cumsum(np.insert(fGns, 0, 0, axis=1), axis=1)

        return ts * spacing[:, None]

