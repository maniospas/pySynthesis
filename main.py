from synthesis import synthesis as synth

lines = synth.import_from("example.py")
test1 = "Calculate PageRank with normalized priors."
test2 = "Calculate PageRank with symmetric normalization and normalized priors."
test3 = "Calculate PageRank with asymmetric normalization and normalized priors."
test4 = "Train and evaluate an SVR model."
test5 = "Train and evaluate and save an SVR model."
test6 = "Train and evaluate and save an SVR model using normalization on training data."

Vstrictness = 1.2#1.1 or 1.2
print(synth.synthesize(test5, lines, Vstrictness)[0])


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