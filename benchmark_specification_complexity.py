from synthesis import synthesis as synth
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
import scipy
from numpy.polynomial.polynomial import polyfit
# additional dependencies for this script: tqdm, numpy, matplotlib

lines = synth.import_from("examples/example.py")
Vstrictness = 1.2

from synthesis.features import tokenize
from time import time
from random import randrange, choices
words = tokenize(" ".join(lines), allow_stopwords=False)
print("Imported", len(lines), "code blocks with", len(words), "words to randomly generate specifications")
print("Benchmarking running time...")
complexities = dict()
for k in tqdm(range(100)):
    for _ in range(100):
        test = " ".join(list(choices(words, k=k)))
        #print(test)
        test_complexity = len(tokenize(test))
        start = time()
        try:
            synth.synthesize(test, lines, Vstrictness)
        except:
            continue
        end = time()
        if test_complexity not in complexities:
            complexities[test_complexity] = list()
        complexities[test_complexity].append(end-start)

complexities, times = [c for c in complexities], [sum(complexities[c])/len(complexities[c]) for c in complexities]
plt.scatter(complexities, times)
b, m = polyfit(complexities, times, 1)
print("Correlation", scipy.stats.pearsonr(complexities, times)[0])
plt.plot(complexities, b + m * np.array(complexities), '-', color='red')
plt.xlabel("Specification complexity")
plt.ylabel("Running time (sec)")
plt.show()