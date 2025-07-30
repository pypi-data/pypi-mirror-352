# Multivariate fractional Brownian motion (mfBm)
This package provides implementation for the multivariate fractional Brownian motion and simple fractional brownian motion with the method described in [1].

### Installation
The mfbm package is available on PyPI and can be install via pip with the following command:
```bash
pip install mfbm
```

### Example usage
```python
import numpy as np
from mfbm import MFBM

p = 5
H = np.linspace(0.6, 0.9, 5)
n = 100
T = 100

rho = 0.7 * np.ones((p, p))
np.fill_diagonal(rho, 1)

eta = np.ones_like(rho)
sigma = np.ones(len(H))

mfbm = MFBM(H, n, rho, eta, sigma)
ts = mfbm.sample(T)
```

![mfbm](https://github.com/user-attachments/assets/32e8242e-11e4-454e-84a8-2bc83b03195c)

[1] Andrew T. A. Wood & Grace Chan (1994): Simulation of Stationary
Gaussian Processes in [0, 1]^d , Journal of Computational and Graphical Statistics, 3:4,
409-432
