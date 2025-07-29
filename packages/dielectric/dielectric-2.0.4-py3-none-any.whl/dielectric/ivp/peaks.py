# https://erdogant.github.io/findpeaks/pages/html/Examples.html#find-peaks-in-low-sampled-dataset
# https://stackoverflow.com/questions/60962094/find-peaks-and-envelope-question-in-python

# Load library
from findpeaks import findpeaks
# Data
X = [9,60,377,985,1153,672,501,1068,1110,574,135,23,3,47,252,812,1182,741,263,33]
# Initialize
fp = findpeaks(lookahead=1)
results = fp.fit(X)
# Plot
fp.plot()

# Initialize with interpolation parameter
fp = findpeaks(lookahead=1, interpolate=10)
results = fp.fit(X)
fp.plot()
