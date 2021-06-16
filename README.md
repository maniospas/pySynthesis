# pySynthesis
This tool enables the automatic synthesis of Python methods by linearly 
combining blocks of existing code whose comments match a provided textual
description (this is considered the synthesis specifications).

The matching mechanism implements a behavioraizeable relation [1] and thus
guarantees that there is an underlying logical system in which synthesis
performs inference. In simple terms, you *can* learn to use this tool to 
easily combine blocks of code

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
outputs the following code:
```python
def solution(x, y, path):
    svr = SVR()
    svr.train(x, y)
    pickle.dump(svr, path)
    y_hat = svr.predict(x, probs=True)
    return svr, scipy.metrics.auc(y, y_hat)
```
Adding textual predicates to the description either adds
or clarifies functionality (to switch to a different).

## Reference
If you reuse or derive code as part of your research, we ask that you cite the following work:
<br/>
**[1]** Emmanouil Krasanakis and Andreas Symeonidis,
*Defining Behaviorizeable Relations to Enable Inference in Semi-Automatic Program Synthesis*,
under review, 2021