#!/usr/bin/env python3

import argparse
import chess
import chess.pgn
import chess.uci
import chess.svg
import urllib.request
import json
import lc0_analyzer
import math
import time

usage_str = ""
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=usage_str)
parser.add_argument("--pgn", type=str, help="pgn file to process")
parser.add_argument("--round", type=str, help="round of pgn file, omit to pick first game")
parser.add_argument("--move", type=float, help="""
4.0 = Before white's 4th move (analyze position after black's 3rd move)
4.5 = Before blacks's 4th move (analyze position after white's 4th move)
""")
parser.add_argument("--numplies", type=int, help="number of plies to analyze")
parser.add_argument("--fen", type=str, help="number of plies to analyze")
parser.add_argument("--fen_desc", type=str, help="description of fen position")
#parser.add_argument("--lc0", type=str, required=True, help="lc0 executable")
#parser.add_argument("--w", type=str, required=True, help="path to weights")
parser.add_argument("--lc0", type=str, required=False, help="lc0 executable")
parser.add_argument("--w", type=str, required=False, help="path to weights")
#parser.add_argument("--nodes", type=int, default=2**16, help="number of nodes to analyze for each position, will be rounded to nearest power of 2")
parser.add_argument("--nodes", type=int, default=2**10, help="number of nodes to analyze for each position, will be rounded to nearest power of 2")
parser.add_argument("--topn", type=int, default=4, help="plot top N moves")
parser.add_argument("--ply_per_page", type=int, default=6, help="how many plies to put together in one .svg page")

args = parser.parse_args()

args.lc0 = "../lc0/build/release/lc0"
args.w = "../lc0nets/32742"
lc0_analyzer.NODES = [ 2**n for n in range(round(math.log(args.nodes, 2))+1)]
lc0_analyzer.NUM_MOVES = args.topn

lc0_analyzer.LC0 = [
    args.lc0,
    "-w", args.w,
    "-l", "lc0log.txt",
    #"-t", "1",
    #"--max-prefetch=0",
    #"--no-out-of-order-eval",   # Was trying to be more accurate, but see issue #680
    #"--collision-visit-limit=1",
    #"--minibatch-size=1",
    "--minibatch-size=16",      # because of #680, use this compromise between accuracy and speed
    "--smart-pruning-factor=0", # We will start and stop in loops, so disable pruning
    "--nncache=1000000",
    "--verbose-move-stats",
]
engine = chess.uci.popen_engine(lc0_analyzer.LC0)
info_handler = lc0_analyzer.Lc0InfoHandler(None)
engine.info_handlers.append(info_handler)

def analyze_current_move(current_ply):
    board = chess.Board()
    with urllib.request.urlopen('https://tcec.chessdom.com/json/live.json') as url:
    #with urllib.request.urlopen('file:./live.json') as url:
        data = json.loads(url.read().decode())
        num_plies = len(data["Moves"])
        print(num_plies)
        if not num_plies == current_ply:
            for m in data["Moves"]:
                board.push_san(m["m"])
            game = chess.pgn.Game.from_board(board)
            filename = "%s__Round_%s.pgn" % (data["Headers"]["Event"], data["Headers"]["Round"])
            open(filename, "w").write(str(game))
            lc0_analyzer.analyze_and_plot(engine, info_handler, filename, None, num_plies-1)
            lc0_analyzer.compose(filename, None, num_plies/2.0+1.0, 1)
    return num_plies

current_ply = -1
while True:
    current_ply = analyze_current_move(current_ply)
    print("sleep")
    time.sleep(15)
