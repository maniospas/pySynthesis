import synthesis as synth

texts = synth.import_from("example.py")
print(synth.synthesize("Train and evaluate and save an SVR model using normalization on training data.", texts, VARIABLE_STRICTNESS=3))