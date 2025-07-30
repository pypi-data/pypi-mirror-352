import numpy as np
from pyhough import pm
from pyhough import hm

# 1 month in chunks of 1024 seconds

sec_per_month = 30*86400;
TFFT = 1800

fmax = 101
fmin = 100
df = 1/TFFT

Nfreqs = (fmax - fmin / df)
spec = pm.simulate_spectrogram(Ntimes, Nfreqs)



times = np.arange(0,sec_per_month,TFFT)
freqs = np.arange(fmin,fmax,df)

Ntimes = len(times)
Nfreqs = len(freqs)

pm_times,pm_freqs,pm_pows,index = pm.make_peakmap_from_spectrogram(times,freqs,spec)

dsd = df/sec_per_month
sig_fdot = 1e-10


sdgrid = hm.make_sd_grid(sig_fdot,dsd) 

Nsds = len(sdgrid)

hmap = hm.hfdf_hough(pm_times,pm_freqs,TFFT,sdgrid)

assert np.shape(hmap) == Nsds, Nfreqs

assert np.all(pm_freqs >= fmin)
assert np.all(pm_freqs <= fmax)
