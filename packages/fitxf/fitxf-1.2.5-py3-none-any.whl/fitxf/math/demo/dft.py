import logging
import numpy as np
import matplotlib.pyplot as plt
from fitxf.math.dsp.Dft import Dft

# no stupid scientific notation
np.set_printoptions(suppress=True)

def MDCT(x: np.ndarray):
    assert len(x) % 2 == 0
    N = int(len(x) / 2)
    # n is indexed at the columns
    n = np.arange(2*N)
    # print(n)
    # reshape so that k is indexed at the rows
    k = np.reshape(np.arange(N), shape=(N, 1))
    # print(k)
    # now we have a k x n matrix
    m = np.cos((np.pi / N) * (n + 1/2 + N/2) * (k + 1/2))
    # x_square = np.array([x.tolist() for i in range(N)])
    # [print(line) for line in np.round(m,3).tolist()]
    y = np.dot(m, x)

    print('Final MDCT length ' + str(len(y)) + ':' + str(y))
    return y

def IMDCT(T: np.ndarray):
    N = len(T)
    # k is indexed at the columns
    k = np.arange(N)
    # print(n)
    # reshape so that n is indexed at the rows
    n = np.reshape(np.arange(2*N), shape=(2*N, 1))
    # print(k)
    # now we have a k x n matrix
    m = (1/N) * np.cos((np.pi / N) * (n + 1/2 + N/2) * (k + 1/2))
    # T_square = np.array([T.tolist() for i in range(2*N)])
    # [print(line) for line in np.round(m,3).tolist()]
    imdct = np.dot(m, T)

    print('Final IMDCT length ' + str(len(imdct)) + ':' + str(imdct))
    return imdct

def plot_fft(X_fft, freq):
    plt.figure(figsize=(8,6))
    plt.stem(freq, abs(X_fft), 'b', markerfmt=' ', basefmt='-b')
    plt.xlabel(r'$\omega$ '+'(Hz)')
    plt.ylabel('DFT Amplitude '+r'$|X(\omega)|$')
    plt.grid(True)
    plt.show()


# sampling rate 100Hz
rate = 30

dft = Dft()

amps = np.array([1, 2, 10])
freqs = np.array([1, 2, 10])
x = dft.getSineSignal(
    samp_rate = rate,
    amps = amps,
    freqs = freqs,
)
print('x shape ' + str(x.shape) + ': ' + str(x))

X_k = dft.DFT(x=x)
print('DFT ' + str(abs(X_k)) + ', shape ' + str(X_k.shape))
N = X_k.size
n = np.arange(N)
# total time span
T = N / rate
freq = n / T
print('N=' + str(N) + ', total time span T=' + str(T))
print('Discrete freq: ' + str(freq))

plot_fft(X_k, freq=freq)
idft = dft.IDFT(y=X_k)
print('Inverse DFT error ' + str(idft - x))
exit(0)

tfm = MDCT(x=x)
N = len(tfm)
n = np.arange(N*2) + 0.5
# total time span
T = 2 * N / rate
freq = n / T
plot_fft(X_fft=tfm, freq=freq[0:N])
i_tfm = IMDCT(T=tfm)
print('Error% IMDCT ' + str(np.round((i_tfm - x) / x, 3).tolist()))

x = np.array([1, 0, 1, 1, 1, 1, 1, 1, 1, 1])
N = 5
# column index
n = np.arange(2 * N)
print(n)
# row index
k = np.reshape(np.arange(N), shape=(N, 1))
print(k)
m = n * k
print(m)
# x_square = np.array([x.tolist() for i in range(N)])
# print(x_square)

y = np.dot(m, x)
print(y)

