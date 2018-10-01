"""Semantris Solver

Usage:
  main.py play [--mode=<mode>] [--verbose]
  main.py (-h | --help)
  main.py --version

Options:
  -h --help      Show this screen
  --version      Show version
  --verbose      Print game activity logs
  --mode=<mode>  Semantris game mode [default: arcade]

"""
import sys
from docopt import docopt

from players.player import Player


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Semantris Solver 0.1')

    # arcade mode player
    if arguments['play'] and arguments['--mode'].lower() == 'arcade':
        Player(mode='arcade', verbose=arguments['--verbose']).run()
    elif arguments['play'] and arguments['--mode'].lower() == 'blocks':
        Player(mode='blocks', verbose=arguments['--verbose']).run()
    else:
        # TODO: Notification message block utility using # characters
        print('Please use either Arcade and Blocks as the game mode')

        # exit game
        sys.exit(0)
