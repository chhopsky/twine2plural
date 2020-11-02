import json
import argparse
from dialogue import Stats, Quest, Gate, Postrouting, Response, Dialogue

parser = argparse.ArgumentParser(description='Convert a twine script to json.')
parser.add_argument('filename', type=str, 
                    help='The filename to import')
parser.add_argument('--output', type=str, 
                    help='Filename to export to (defaults to same filename but .json')
args = parser.parse_args()

dialogue_adv = []
dialogue_map = {}

with open(args.filename, r) as f:
    for line in f:
        if line.startswith("::"):
            # we are at the start of a new dialogue line

