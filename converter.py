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
import math
import argparse
from collections import OrderedDict
import svgutils.transform as sg
from svgutils.compose import *
#import cairosvg

moves = "e2e4 c7c6 d2d4 d7d5 e4e5 c8f5 f1e2 e7e6 g1f3 f8b4 c2c3 b4e7 c1e3 b8d7 e1g1 f5g6 b1d2 g8h6 e3h6 g7h6 d2b3 f7f6 e5f6 e7d6 d1d2 d8f6 d2h6 e8c8 a1e1 h8g8 e2d1 d8f8 g2g3 g6f5 h6f6 d7f6 f3h4 f5h3 h4g2 h7h5 e1e3 h5h4 g2h4 h3f1 g1f1 c8d7 f1g2 f6g4 d1g4 g8g4 h4f3 b7b6 h2h3 g4g7 b3c1 d6f4 e3e1 f4c1 e1c1 c6c5 g3g4 d7d6 c1c2 f8f4 g2g3 f4e4 c2d2 d6e7 f3e5 e4e1 h3h4 a7a5 h4h5 e1g1 g3f4 g7g8 f2f3 e7f6 d2h2 f6g7 e5g6 g7f6 g6e5 f6g7 e5g6 g1f1 h2e2 g8e8 g6e5 e8f8 f4g5 f1g1 e5g6 f8f5 g5h4 g1h1 h4g3 f5f6 g6h4 c5d4 c3d4 h1g1 h4g2 f6h6 g3h2 g1d1 g2f4 h6f6 f4e6 g7f7 e6g5 f7g8 h2g3 d1g1 g3h2 g1a1 a2a3 a1d1 h2g3 d1g1 g3h3 b6b5 e2e8 f6f8 e8e6 g1d1 h5h6 b5b4 a3b4 a5b4 h3h4 d1h1 h4g3 b4b3 e6b6 h1g1 g3h2 g1a1 b6b3 a1a6 h6h7 g8h8 h2g3 a6a8 f3f4 a8b8 b3c3 b8b2 f4f5 b2b7 g3f4 b7e7 c3c6 e7e2 c6d6 e2f2 f4g3 f2f1 d6d5 f1g1 g3f4 g1f1 f4e3 f8e8 d5e5 e8f8 e5e6 f1d1 e6d6 f8e8 e3f3 d1f1 f3g2 f1f4 g2g3 f4f1 d6e6 e8b8 e6g6 b8b3 g3g2 b3b2 g2f1".split()

board = chess.Board()
for m in moves:
    board.push_uci(m)
game = chess.pgn.Game.from_board(board)
print(game)

