#!/usr/bin/env python3

#
# Usage: see lc0_graph_activations.py --help
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
import sys
#import cairosvg

COLS = 32
ROWS = 8

DIR_VECTORS = {'N': (0, 1), 'NE': (1, 1), 'E': (1, 0), 'SE': (1, -1),
        'S':(0, -1), 'SW':(-1, -1), 'W': (-1, 0), 'NW': (-1, 1)}

KNIGHT_DIR_VECTORS = {'N': (1, 2), 'NE': (2, 1), 'E': (2, -1), 'SE': (1, -2),
        'S':(-1, -2), 'SW':(-2, -1), 'W': (-2, 1), 'NW': (-1, 2)}

LOCMAP = []

for direction in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
    for steps in range(1, 8):
        x, y = DIR_VECTORS[direction]
        x *= steps
        y *= steps
        #print(len(LOCMAP), "normal", direction, x, y)
        LOCMAP.append((x, y))

for direction in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
    x, y = KNIGHT_DIR_VECTORS[direction]
    #print(len(LOCMAP), "knight", direction, x, y)
    LOCMAP.append((x,y))

LOCMAP.extend([(-5,8),(-4,8),(-3,8), (-1,8),(0,8),(1,8), (3,8),(4,8),(5,8)])

def plot(data, layernum, board):
    if len(data) == 80:
        fig, ax = plt.subplots(16, 15, figsize=(15*2,16*2), subplot_kw={'title':"", 'xticks':[], 'yticks':[]}, frameon=False)
        for e, d in enumerate(data):
            if e >= len(LOCMAP): break
            # Data in logfile has side to move going down the board,
            # so flip vertically.
            d = np.flip(d, 0)
            x, y = LOCMAP[e]
            x += 7
            y = -y + 8
            #ax[y, x].imshow(d, norm=matplotlib.colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=-50, vmax=50))
            ax[y, x].imshow(d, norm=matplotlib.colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=-1, vmax=1))
            #ax[y, x].imshow(d, vmin=0, vmax=1)
            #ax[y, x].imshow(d, norm=matplotlib.colors.Normalize(vmin=0., vmax=1.))
            ax[y, x].get_xaxis().set_visible(False)
            ax[y, x].get_yaxis().set_visible(False)
        #plt.tight_layout(w_pad=0.01, h_pad=0.01)
        filename = "%s/activation_layer_%03d.png" % (args.savedir, layernum)
        plt.savefig(filename, transparent=True)
        plt.close("all")
        print("saved " + filename)
    else:
        fig, ax = plt.subplots(ROWS, COLS, figsize=(32,8), subplot_kw={'title':"", 'xticks':[], 'yticks':[]}, frameon=False)
        for e, d in enumerate(data):
            # Data in logfile has side to move going down the board,
            # so flip vertically.
            d = np.flip(d, 0)
            #ax[e//COLS, e%COLS].imshow(d, norm=matplotlib.colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=-50, vmax=50))
            ax[e//COLS, e%COLS].imshow(d, norm=matplotlib.colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=-1, vmax=1))
            #ax[e//COLS, e%COLS].imshow(d, vmin=0, vmax=1)
            ax[e//COLS, e%COLS].get_xaxis().set_visible(False)
            ax[e//COLS, e%COLS].get_yaxis().set_visible(False)
        plt.tight_layout(w_pad=0.01, h_pad=0.01)
        filename = "%s/activation_layer_%03d.png" % (args.savedir, layernum)
        plt.savefig(filename, transparent=True)
        plt.close("all")
        print("saved " + filename)

def parse():
    alldata = []
    layernum = 0
    board = chess.Board()
    if not os.path.exists(args.savedir):
        os.makedirs(args.savedir)
    for line in open(args.logfile).readlines():
        m = re.search(">> position startpos", line)
        if m:
            m = re.search(">> (position startpos moves .*)", line)
            if m:
                ucipos = m.group(1)
            else:
                ucipos = "position startpos"
            f = open("%s/activation_game.txt" % (args.savedir), "w")
            for m in ucipos.split()[3:]:
                board.push_uci(m)
            f.write(str(chess.pgn.Game.from_board(board)) + "\n")
            f.write(str(ucipos) + "\n")
            f.write(str(board.fen()) + "\n")
            f.write(str(board) + "\n")
            f.close()
        data = line.split()
        if len(data) == 0 or not data[0].startswith("channel:"): continue
        _,channel_num = data[0].split(":")
        channel_num = int(channel_num)
        if channel_num == 0 and len(alldata) > 0:
            plot(alldata, layernum, board)
            alldata = []
            layernum += 1
        data = [float(x) for x in data[1:]]
        alldata.append(np.array(data).reshape((8,8)))
    plot(alldata, layernum, board)

if __name__ == "__main__":
    usage_str = """
lc0_graph_activations.py lc0log_mypos.txt activations_mypos

This script parses a logfile generated using a special lc0 binary that dumps
activation data of the NN. It outputs a text file of the position, and images
of the activations for every layer of the NN.

To generate a logfile:
* `git clone -b nndebug http://github.com/killerducky/lc0`
* Build lc0
* Run lc0 with Backend=blas, and LogFile=lc0log_mypos.txt
* setposition you want to analyze
  * currently script assumes there is only 1 position!
  * fens won't work right now, only full setposition
* go nodes 1 (it's important the NN only analyzes one position)
* quit lc0
* Now you can run this script on lc0log_mypos.txt


Side to move is always going up in these images.

Output files generated:

activation_game.txt - pgn, uci, fen, and ascii board
activation_layer_000.png - Inputs:
    For 8 plies of hisory, most recent first:
        Our     P, N, B, R, Q, K
        Their   P, N, B, R, Q, K
        Repetition plane
    We can O-O-O
    We can O-O
    They can O-O-O
    They can O-O
    We are Black
    50 move rule counter
    Unused (used to be move count)
    Plane of 1s
activation_layer_001.png - Output of input convolution
activation_layer_002.png - Output of 1st resblock, first half
activation_layer_003.png - Output of 1st resblock, second half
...
activation_layer_040.png - Output of 20th resblock, second half
activation_layer_041.png - Output of 20th resblock, second half
activation_layer_042.png - Output of Policy FC layer (T50 convolutional Policy will have two convolves instead)
(Final Policy move selection not supported yet)
"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage_str)
    parser.add_argument("logfile", type=str, help="logfile to parse")
    parser.add_argument("savedir", type=str, help="directory to put files")

    args = parser.parse_args()
    print(args.logfile)
    parse()
