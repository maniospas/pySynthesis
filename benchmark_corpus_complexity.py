from synthesis import synthesis as synth
from synthesis.analysis import get_expressions
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
import scipy
from numpy.polynomial.polynomial import polyfit
# additional dependencies for this script: tqdm, numpy, matplotlib

def import_from(file, limit=None):
    if file[-3:] != ".py":
        return []
    lines = list()
    with open(file) as f:
        accum = ""
        i = 0
        for line in f:
            if line.strip().startswith("def ") and len(accum)>0:
                lines.append(accum)
                accum = ""
            accum += line
            i += 1
            if limit is not None and i==limit:
                break
        lines.append(accum)
    return lines, i

all_lines, num_all_lines = import_from("examples/example.py")
Vstrictness = 1.2
print("total lines", num_all_lines)

from synthesis.features import tokenize
from time import time
from random import randrange, choices
words = tokenize(" ".join(all_lines), allow_stopwords=False)
print("Imported", len(words), "lines of code")
print("Benchmarking running time...")
complexities = dict()
for num_lines in tqdm(range(1, num_all_lines)):
    lines = import_from("examples/example.py", num_lines)[0]
    test_complexity = sum(len(tokenize(line.lstrip(), False)) for bl in lines for line in get_expressions(bl) if len(line)>0 and line.lstrip()[0]=="#")
    print(test_complexity)
    if test_complexity==0:
        continue
    for k in range(100):
        test = " ".join(list(choices(words, k=k)))
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
plt.xlabel("Total Code Comment Expressions")
plt.ylabel("Running time (sec)")
plt.show()