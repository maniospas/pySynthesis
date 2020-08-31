import synthesis as synth

texts = synth.import_from("example.py")
test1 = "Calculate PageRank with normalized priors."
test2 = "Calculate PageRank with asymmetric normalization and normalized priors."
test3 = "Train and evaluate and save an SVR model using normalization on training data."
print(synth.synthesize(test2, texts, None))