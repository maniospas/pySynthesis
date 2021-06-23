from synthesis import synthesis as synth
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
import scipy
from numpy.polynomial.polynomial import polyfit
from synthesis.features import tokenize
from time import time
from random import randrange, choices, seed
# additional dependencies for this script: tqdm, numpy, matplotlib

lines = synth.import_from("examples/example.py")
Vstrictness = 1.2

seed(1) # reproducibility

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

avg_times = [sum(complexities[c])/len(complexities[c]) for c in complexities]
std_times = [np.std(np.array(complexities[c])) for c in complexities]
max_times = [np.max(np.array(complexities[c])) for c in complexities]
complexities = [c for c in complexities]

plt.errorbar(complexities, avg_times, np.array(std_times), linestyle='None', marker='o')
b, m = polyfit(complexities, avg_times, 1)
print("Correlation with avg", scipy.stats.pearsonr(complexities, avg_times)[0])
print("Correlation with std", scipy.stats.pearsonr(complexities, std_times)[0])
plt.plot(complexities, b + m * np.array(complexities), '-', color='red')
plt.xlabel("Problem specification complexity")
plt.ylabel("Running time (sec)")
plt.show()