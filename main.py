from synthesis import synthesis as synth

lines = synth.import_from("example.py")
test1 = "Calculate PageRank."
test2 = "Calculate PageRank with normalized priors."
test3 = "Calculate PageRank with symmetric normalization and normalized priors."
test4 = "Calculate PageRank with asymmetric normalization and normalized priors."

test5 = "Train a model."
test6 = "Train an SVR model."
test7 = "Train and evaluate an SVR model."
test8 = "Train and evaluate and save an SVR model."
test9 = "Train and evaluate and save an SVR model using normalization on training data."
test10 = "Train and evaluate a logistic regression model using standardization on training data."

Vstrictness = 1.2#1.1 or 1.2
print(synth.synthesize(test9, lines, Vstrictness)[0])

from synthesis.features import tokenize
from time import time
from random import randrange, choices
words = tokenize(" ".join(lines), allow_stopwords=False)
print(len(words))

complexities = list()
times = list()
for k in range(100):
    for _ in range(4):
        test = " ".join(list(choices(words, k=k)))
        test_complexity = len(tokenize(test))
        print(test_complexity)
        try:
            synth.synthesize(test, lines, Vstrictness)
        except:
            continue
        start = time()
        for _ in range(20):
            synth.synthesize(test, lines, Vstrictness)
        end = time()
        complexities.append(str(test_complexity))
        times.append(str((end-start)/20.))
print("complexities = ["+" ".join(complexities)+"]")
print("times = ["+" ".join(times)+"]")

"""
formal_lines = synth.import_from("formal_example.py")
formal_test1 = "return the greatest between a number and zero"
formal_test2 = "return the greatest between a number and its negative"
formal_test3 = "return the greatest between a random number and its negative"
formal_test4 = "return the greatest between a random number and zero"
formal_test5 = "return the negative of the greatest between a random number and zero"
formal_test6 = "return the negative of the greatest between a random number and its negative"
print(synth.synthesize(formal_test2, formal_lines, -1, single_output=True))#or .8 or 1.6
"""