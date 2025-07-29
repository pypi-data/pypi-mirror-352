import numpy as np
from typing import Optional

class FBM:
    def __init__(self, H: float, n: int, T: float):
        self.H = H
        self.n = n
        self.T = T
        self.circulant_row: Optional[np.ndarray] = None
        self.sqrt_eigens: Optional[np.ndarray] = None

    def calculate_eigen_decomposition(self):
        self.circulant_row = np.zeros(self.n + 1)
        self.circulant_row[0] = 1

        i = np.arange(1, self.n + 1)
        self.circulant_row[1:] = 0.5 * ((i + 1) ** (2 * self.H) - 2 * i ** (2 * self.H) + ((i - 1) ** (2 * self.H)))

        self.circulant_row = np.concatenate([self.circulant_row, np.flip(self.circulant_row[1:-1])])

        lmbd = np.real(np.fft.fft(self.circulant_row) / (2 * self.n))
        self.sqrt_eigens = np.sqrt(lmbd)

    def sample(self):
        if self.circulant_row is None or self.sqrt_eigens is None:
            self.calculate_eigen_decomposition()

        noise = np.random.normal(size=2 * self.n) + np.random.normal(size=2 * self.n) * 1j

        W = np.fft.fft(self.sqrt_eigens * noise)
        W = self.n ** (-self.H) * np.cumsum(np.concatenate(([0], np.real(W[1:(self.n + 1)]))))

        W = (self.T ** self.H) * W
        return W

