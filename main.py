import synthesis as synth

texts = synth.import_from("example.py")
print(synth.synthesize("Calculate PageRank with asymetric normalization and normalized priors.", texts))