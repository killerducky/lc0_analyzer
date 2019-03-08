#!/usr/bin/env python3

#
# 32930	2	5c222ccd	3287.00	32406	20	256	2019-01-28 00:59:32 +00:00	3287
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
import sys


path = sys.argv[1]
files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
stats = {}
stats["LEGAL_L"] = 0
stats["LEGAL_N"] = 0
stats["LEGAL_R"] = 0
stats["GAME_L"] = 0
stats["GAME_N"] = 0
stats["GAME_R"] = 0
stats["TOTAL_PROMOTE"] = 0
stats["TOTAL_PLIES"] = 0
stats["TOTAL_GAMES"] = 0
for l in (False, True):
    for n in (False, True):
        for r in (False, True):
            stats[(l,n,r)] = 0
            for game in ("L", "N", "R"):
                stats[(l,n,r,game)] = 0
                stats[(l,n,r,game)] = 0
                stats[(l,n,r,game)] = 0
TOTAL_TOTAL = 7
for pgnfile in files:
    stats["TOTAL_GAMES"] += 1
    pgn = open(pgnfile)
    game = chess.pgn.read_game(pgn)
    nodes = list(game.mainline())
    board = game.board()
    for node in nodes:
        stats["TOTAL_PLIES"] += 1
        if node.move.promotion:
            legal_moves = list(board.legal_moves)
        board.push(node.move)
        if node.move.promotion:
            stats["TOTAL_PROMOTE"] += 1
            print(board)
            ff = chess.square_file(node.move.from_square)
            #rf = chess.square_rank(node.move.from_square)
            ft = chess.square_file(node.move.to_square)
            rt = chess.square_rank(node.move.to_square)
            pnorm = chess.Move(node.move.from_square, chess.square(ff, rt), promotion=chess.QUEEN) in legal_moves
            pleft = ff > 0 and chess.Move(node.move.from_square, chess.square(ff-1, rt), promotion=chess.QUEEN) in legal_moves
            pright = ff < 7 and chess.Move(node.move.from_square, chess.square(ff+1, rt), promotion=chess.QUEEN) in legal_moves
            if pleft: stats["LEGAL_L"] += 1
            if pnorm: stats["LEGAL_N"] += 1
            if pright: stats["LEGAL_R"] += 1
            stats[(pleft, pnorm, pright)] += 1
            if ff-1 == ft: 
                stats["GAME_L"] += 1
                stats[(pleft, pnorm, pright, "L")] += 1
            if ff   == ft: 
                stats["GAME_N"] += 1
                stats[(pleft, pnorm, pright, "N")] += 1
            if ff+1 == ft: 
                stats["GAME_R"] += 1
                stats[(pleft, pnorm, pright, "R")] += 1
            print(node.move, pleft, pnorm, pright, stats)
            print()

  
