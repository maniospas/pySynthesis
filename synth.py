import argparse
from synthesis import synthesis as synth

parser = argparse.ArgumentParser(description='pySynthesis: linearly combine blocks of Python code based on their comments.')
parser.add_argument('specs', type=str, help='Textual description of the desired method to create.')
parser.add_argument('code', type=str, default='.', help='File or folder path where example code resides.')
parser.add_argument('--vstrict', type=float, default=1.1, help='Empirical variable strictness threshold to merge variables (default is 1.1).')
parser.add_argument('--name', type=str, default='solution', help='Custom name of defined method.')

args = parser.parse_args()
lines = synth.import_from(args.code)
code = synth.synthesize(args.specs, lines, args.vstrict)[0]
code = code.replace("def solution", "def "+args.name)
print(code)