from synthesis import synthesis as synth

lines = synth.import_from("example.py")
test1 = "Calculate PageRank with normalized priors."
test2 = "Calculate PageRank with asymmetric normalization and normalized priors."
test3 = "Train and evaluate an SVR model."
test4 = "Train and evaluate and save an SVR model using normalization on training data."
print(synth.synthesize(test4, lines, 1))