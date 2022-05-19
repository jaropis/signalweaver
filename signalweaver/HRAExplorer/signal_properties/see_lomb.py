# I am trying to figure out the correct scale for the periodogram

import numpy as np
import scipy.signal as signal
from scipy import sum, var
import pylab as plt

def test_lomb_scargle(skala = 2*np.pi, frac_points=0.9, nout=1000, predicted_spectral_content = 2*np.pi):
    A = 8.
    w = 1.
    phi = 0.5 * np.pi
    nin = 1000
    r = np.random.rand(nin)
    x = np.linspace(0.01, skala, nin)
    print(len(x))
    x = x[r <= frac_points]
    normval = x.shape[0] # For normalization of the periodogram
    y = A * np.sin(w*x+phi)
    f = np.linspace(0.01, predicted_spectral_content, nout)

    pgram = signal.lombscargle(x, y, f)
    plt.subplot(2,1,1)
    plt.plot(x, y, '-')
    plt.subplot(2,1,2)
    plt.plot(f, pgram, 'b-')
    plt.show()
    var_psd = sum(4*pgram[f <= predicted_spectral_content*1.3]/normval)*(f[1] - f[0]) * skala/(2*np.pi)/2
    var_signal = var(y)
    print(len(x), normval, skala)
    return var_signal, var_psd
test_lomb_scargle()
