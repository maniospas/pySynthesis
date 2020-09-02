from synthesis import synthesis as synth

lines = synth.import_from("example.py")
test1 = "Calculate PageRank with normalized priors."
test2 = "Calculate PageRank with symmetric normalized priors."
test3 = "Calculate PageRank with asymmetric normalization and normalized priors."
test4 = "Train and evaluate and save an SVR model."
test5 = "Train and evaluate and save an SVR model using normalization on training data."
print(synth.synthesize(test1, lines, .8))#or .8 or 1.6