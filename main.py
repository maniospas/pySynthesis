import synthesis as synth

texts = synth.import_from("example.py")
print(synth.synthesize("Calculate PageRank with asymmetric normalization and normalized priors.", texts, VARIABLE_STRICTNESS=5))