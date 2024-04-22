import numpy as np
import numba
import matplotlib.pyplot as plt

class ImpulseResponse:
    def __init__(self, N, Mrn, Mpn, gamma, pnv, rn):
        self.N = N
        self.Mrn = Mrn
        self.Mpn = Mpn
        self.gamma = gamma
        self.pnv = pnv
        self.rn = rn
        self.tau = [rn[i] / 3e8 for i in range(N)]

    @staticmethod
    @numba.njit
    def vectorized_sinc(x, dtype=np.float64):
        return np.sin(np.pi * x) / (np.pi * x)

    @staticmethod
    @numba.njit
    def sinc_jitted(x, y, shape):
        for i in numba.prange(shape[0]):
            if abs(x[i]) < 1e-10:
                y[i] = 1.0
            else:
                y[i] = ImpulseResponse.vectorized_sinc(x[i])

    def calculate_impulse_response(self, t):
        h = np.zeros_like(t, dtype=complex)
        gamma_pnv_prod = np.zeros(self.N, dtype=complex)
        for n in range(self.N):
            gamma_pnv_prod[n] = (self.gamma[n] ** self.Mrn[n]) * (self.pnv[n] ** self.Mpn[n]) / self.rn[n]
        t_max = t.max()
        ImpulseResponse.sinc_jitted(t - self.tau, h, t.shape)
        h *= np.exp(-1j * 2 * np.pi * self.tau / t_max) * gamma_pnv_prod
        return h

    def calculate_fourier_transform(self, t, h):
        freq = np.fft.fftfreq(len(t), t[1] - t[0])
        H = np.fft.fft(h)
        return freq, H

    def plot_impulse_response(self, t, h):
        plt.figure(figsize=(10, 6))
        plt.plot(t * 1e9, np.abs(h))
        plt.xlabel('Tiempo (ns)')
        plt.ylabel('Amplitud')
        plt.title('Respuesta al impulso h(t)')
        plt.grid(True)
        plt.show()

    def plot_fourier_transform(self, freq, H):
        plt.figure(figsize=(10, 6))
        plt.plot(freq * 1e-9, np.abs(H))
        plt.xlabel('Frecuencia (GHz)')
        plt.ylabel('Magnitud')
        plt.title('Transformada de Fourier de h(t)')
        plt.grid(True)
        plt.show()