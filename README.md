# pySynthesis
This tool enables the automatic synthesis of Python methods by linearly 
combining blocks of existing code whose comments match a provided textual
description (this is considered the synthesis specifications). 
The matching mechanism implements a behaviorizeable relation [1] and thus
guarantees that there is an underlying logical system in which synthesis
performs inference. In simple terms, you *can* learn to use this tool to 
easily combine blocks of code.

**Dependencies**
<br/>
nltk

**Contact**
<br/>
Emmanouil (Manios) Krasanakis, manios.krasanakis@issel.ee.auth.gr

## Usage
Install Python and necessary dependencies, open a terminal
in the project's folder and run the command:
`python synth.py -h` to view all possible arguments.
For example, to synthesize the following quoted phrase
based on a file of example implementations, run:
```bash
python synth.py "train and evaluate and save an SVR model" examples/example.py
```
This outputs the following code:
```python
def solution(x, y, path):
    svr = SVR()
    svr.train(x, y)
    pickle.dump(svr, path)
    y_hat = svr.predict(x, probs=True)
    return svr, scipy.metrics.auc(y, y_hat)
```
Adding textual predicates to the description either adds
or clarifies functionality (to switch to a different implementation).

A list of interesting queries that can be synthesized 
from the example code file (try --vstrict 1.1 and --vstrict 1.2):
```
"Calculate PageRank."
"Calculate PageRank with normalized priors."
"Calculate PageRank with symmetric normalization and normalized priors."
"Calculate PageRank with asymmetric normalization and normalized priors."

"Train a model."
"Train an SVR model."
"Train and evaluate an SVR model."
"Train and evaluate a logistic regression model."
"Train, evaluate and save an SVR model."
"Train and evaluate and save an SVR model using normalization on training data."
"Train and evaluate a logistic regression model using standardization on training data."
```

## GUI
Run the file *synthui.py* to perform synthesis with a GUI.

https://user-images.githubusercontent.com/2576023/196159267-48079c19-c4c8-418c-8037-0dd9add56b0b.mp4


## Reference
If you reuse or derive code as part of your research, we ask that you cite the following work:

```
@article{krasanakis2021defining,
  title={Defining Behaviorizeable Relations to Enable Inference in Semi-Automatic Program Synthesis},
  author={Krasanakis, Emmanouil and Symeonidis, Andreas},
  journal={Journal of Logical and Algebraic Methods in Programming},
  pages={100714},
  year={2021},
  publisher={Elsevier}
}
```

## Exposing Internal Steps
To expose how synthesis works, add the `--show-known` option. To display imported code blocks
add the `--verbose` option to show intermediate steps. To avoid renaming intermediate variables
and thus keep compatible variable names between the two options, use `--explain` instead of the
second one. For example: 
```bash
python synth.py "pagerank with symmetric normalization" examples/example.py --explain --show-known
```

:warning: The `--explain` option could introduce erroneous synthesis outcomes 
if the same code block is added more than one time to the synthesized program
(this should happen only rarely and typically means that specifications were
misunderstood).

## Benchmarks
Benchmarks additionally depend on the *tqdm,numpy,matplotlib* libraries.
After installing these, the running time measurements of our 
paper can be replicated by the scripts:
- `benchmark_specification_complexity.py`
to analyse how synthesis time scales with user specification complexity
- `benchmark_corpus_complexity.py` 
to analyse how synthesis time scales with the total complexity of known specifications
in corpora of various sizes

# New Examples
```
python synth.py "run default personalized pagerank from a small graph's signal and assess it on a signal split" examples\pygrank_snippets.py
```

```
"run personalized pagerank"
"run default personalized pagerank"
```
