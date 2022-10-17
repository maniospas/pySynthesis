import argparse
import os
from synthesis import synthesis as synth

parser = argparse.ArgumentParser(description='pySynthesis: linearly combine blocks of Python code based on their comments.')
parser.add_argument('specs', type=str, help='Textual description of the desired method to create.')
parser.add_argument('code', type=str, default='.', help='File or folder path where example code resides.')
parser.add_argument('--vstrict', type=float, default=1.1, help='Empirical variable strictness threshold to merge variables (default is 1.1).')
parser.add_argument('--name', type=str, default='solution', help='Custom name of defined method.')
parser.add_argument('--show-known', action="store_true", help='Output known code blocks.')
parser.add_argument('--verbose', action="store_true", help='Output intermediate steps during synthesis. Prefer --explain to understand')
parser.add_argument('--explain', action="store_true", help='Can yield WRONG RESULT if same code block used multiple times. '+
                                                           'Forces synthesis to retain original variable names '+
                                                           '(makes --verbose and --show-known display compatible variable names)'
                                                           'and automatically toggles --verbose.')

args = parser.parse_args()
lines = synth.import_from(args.code)
if len(lines) == 0:
    for (dirpath, dirnames, filenames) in os.walk(args.code):
        for file in filenames:
            path = os.path.join(dirpath, file)
            if "venv" not in path:
                lines += synth.import_from(path)
#try:
if len(lines) == 0:
    raise Exception("No source code imported")
code = synth.synthesize(args.specs, lines, args.vstrict,
                        verbose=args.verbose or args.explain,
                        show_known=args.show_known,
                        rename_after_each_step=not args.explain)[0]
code = code.replace("def solution", "def "+args.name)
print(code)
#except:
    #print("Could not match description (specs) to any source code comments")