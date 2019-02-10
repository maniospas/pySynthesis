import synthesis as synth

texts = synth.import_from("example.py")
print(synth.synthesize("Train, evaluate and dump an SVR.", texts))