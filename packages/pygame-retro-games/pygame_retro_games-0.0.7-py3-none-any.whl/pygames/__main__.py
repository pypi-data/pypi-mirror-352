from argparse import ArgumentParser
from pygames.bounce.main import run as bounce

parser = ArgumentParser(description='PyGame Retro Games')
parser.add_argument('cmd', choices=['bounce'])
args = parser.parse_args()
if args.cmd == 'bounce':
    bounce()
