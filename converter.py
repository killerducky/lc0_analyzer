#!/usr/bin/env python3

#
# lc0_analyzer.py --help
#
# See https://github.com/killerducky/lc0_analyzer/README.md for description
#
# See example.sh
#

import chess
import chess.pgn
import chess.uci
import chess.svg
import re
import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd
import numpy as np
import os
import sys
import math
import argparse
from collections import OrderedDict
import svgutils.transform as sg
from svgutils.compose import *
#import cairosvg

#moves = "e2e4 c7c6 d2d4 d7d5"

board = chess.Board()
for m in sys.argv[1:]:
    board.push_uci(m)
game = chess.pgn.Game.from_board(board)
print(game)

