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


class Lc0InfoHandler(chess.uci.InfoHandler):
    def __init__(self, board):
        super().__init__()
        self.reset()
        self.board = board
    def reset(self):
        self.strings = []
        self.moves = {}
    def post_info(self):
        if "string" in self.info:
            #self.strings.append(self.info["string"])
            # "c7f4  (268 ) N:      40 (+37) (P: 20.23%) (Q: -0.04164) (U: 0.08339) (Q+U:  0.04175) (V:  0.1052)"
            (move, info) = self.info["string"].split(maxsplit=1)
            move = self.board.san(self.board.parse_uci(move))
            self.strings.append("%6s %s" % (move, self.info["string"]))
        super().post_info() # Release the lock

def q2cp(q):
    return 290.680623072 * math.tan(1.548090806 * q) / 100.0

def cp2q(cp):
    return math.atan(cp*100.0/290.680623072)/1.548090806

def set_q2cp_ticks(ax):
    ax.set_ylim(-1, 1)
    ax2 = ax.twinx()
    ax2.set_ylim(-1, 1)
    cp_vals = [-128, -8, -4, -2, -1, 0, 1, 2, 4, 8, 128]
    q_vals  = [cp2q(x) for x in cp_vals]
    ax2.set_yticks(q_vals)
    ax2.set_yticklabels(cp_vals)
    ax2.set_ylabel("CP")

def parse_info(info):
    # "INFO: TN: 1   Qf4 c7f4  (268 ) N:      40 (+37) (P: 20.23%) (Q: -0.04164) (U: 0.08339) (Q+U:  0.04175) (V:  0.1052)"
    m = re.match("^INFO:", info)
    if not m: return None
    (_, _, TN, sanmove, ucimove, info) = info.split(maxsplit=5)
    floats = re.split(r"[^-.\d]+", info)
    (_, _, N, _, P, Q, U, Q_U, V, _) = floats
    move_infos = {}
    move_infos["TN"] = int(TN)
    move_infos["sanmove"] = sanmove
    move_infos["ucimove"] = ucimove
    move_infos["N"] = int(N)
    move_infos["P"] = float(P)
    move_infos["Q"] = float(Q)
    move_infos["U"] = float(U)
    if V == "-.----": V = 0
    move_infos["V"] = float(V)
    return move_infos

def getgame(pgn_filename, gamenum):
    with open(pgn_filename) as pgn:
        # find the game (probably a better way to do this?)
        game = None
        while True:
            game = chess.pgn.read_game(pgn)
            if not game:
                break
            if not gamenum or game.headers["Round"] == gamenum:
                break
        if not game:
            raise("Game not found")
    return game

# plynum =        0 = after White's move 1
# plynum =        1 = after Black's move 1
# plynum = 2(M-1)+0 = after White's move M
# plynum = 2(M-1)+1 = after Black's move M
def get_board(pgn_filename, gamenum, plynum):
    game = getgame(pgn_filename, gamenum)
    info = ""
    info += game.headers["White"] + "\n"
    info += game.headers["Black"] + "\n"
    nodes = list(game.mainline())
    # There must be a better way to get the list of moves up to plynum P?
    ucistr = ""
    sanstr = ""
    if plynum >= 0:
        for node in nodes[0:plynum+1]:
            ucistr += " " + str(node.move)
            sanstr += " " + str(node.san())
        info += "position startpos moves" + ucistr + "\n"
        info += sanstr + "\n"  # TODO: Add move numbers. Surely python-chess can do this for me?
        # Something like this will work...
        #game = getgame(pgn_filename, gamenum)
        #end = game.end()
        #board = end.board()
        #print(game.board().variation_san(board.move_stack))
        node = nodes[plynum]
        board = node.board()
        fig = chess.svg.board(board=board, lastmove=node.move)
    else:
        info += "position startpos\n"
        board = chess.Board()
        fig = chess.svg.board(board=board)
    return (board, fig, info)

# TODO:
# gamenum/plynum vs fen is a mess right now...
def analyze_and_plot(engine, info_handler, pgn_filename, gamenum, plynum, fen=None):
    analyze(engine, info_handler, pgn_filename, gamenum, plynum, fen)
    plot(pgn_filename, gamenum, plynum)

def analyze(engine, info_handler, pgn_filename, gamenum, plynum, fen=None):
    savedir = "plots/%s_%s_%05.1f" % (pgn_filename, gamenum, (plynum+3)/2.0)
    datafilename = "%s/data.html" % (savedir)
    if os.path.exists(datafilename):
        return
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    outfile = open(datafilename, "w")
    outfile.write("""
<img src="board.svg" height="100%"/> <br>
<img src="Q.svg"/> <br>
<img src="Q2.svg"/> <br>
<img src="N.svg"/> <br>
<img src="P.svg"/> <br>
<pre>""")
    if fen:
        board = chess.Board(fen)
        fig = chess.svg.board(board=board)
        info = "position %s\n" % (fen)
    else:
        (board, fig, info) = get_board(pgn_filename, gamenum, plynum)
    outfile.write(info)
    outfile.write(board.fen() + "\n")
    outfile.write(str(board) + "\n")
    open("%s/board.svg" % (savedir), "w").write(fig)
    outfile.write(str(LC0) + "\n")
    engine.uci()
    outfile.write(engine.name + "\n")
    # Reset engine search tree, but not engine NNCache, by setting different position
    engine.position(chess.Board())
    info_handler.reset()
    info_handler.board = chess.Board()
    engine.go(nodes=1)
    for nodes in NODES:
        # Do our position now
        info_handler.reset()
        info_handler.board = board
        engine.position(board)
        engine.go(nodes=nodes)
        for s in info_handler.strings:
            outfile.write("INFO: TN: %s %s\n" % (nodes, s))
    outfile.write("</pre>\n")
    outfile.close()

def plot(pgn_filename, gamenum, plynum):
    savedir = "plots/%s_%s_%05.1f" % (pgn_filename, gamenum, (plynum+3)/2.0)

    # Parse data into pandas
    move_infos = []
    with open("%s/data.html" % savedir) as infile:
        for line in infile.readlines():
            info = parse_info(line)
            if not info: continue
            move_infos.append(info)
    df = pd.DataFrame(move_infos)

    # Filter top 4 moves, and get P
    TNmax = df["TN"].max()
    best = df[df["TN"] == TNmax].sort_values("N", ascending=False).head(NUM_MOVES)
    moves = list(best["sanmove"])
    bestdf = df.loc[df["sanmove"].isin(moves)]

    # Plots
    fig, ax = plt.subplots()
    for move in moves:
        tmp = bestdf[bestdf["sanmove"] == move]
        tmp.plot.line(x="TN", y="N", logx=True, logy=True, ax=ax)
    ax.legend(moves)
    plt.title("Child Node Visits vs Total Nodes")
    plt.xlabel("Total Nodes")
    plt.ylabel("Child Nodes")
    plt.savefig("%s/N.svg" % (savedir))

    fig, ax = plt.subplots()
    for move in moves:
        tmp = bestdf[bestdf["sanmove"] == move]
        tmp.plot.line(x="TN", y="Q", logx=True, logy=False, ax=ax)
    ax.legend(moves)
    plt.title("Value vs Total Nodes")
    plt.xlabel("Total Nodes")
    plt.ylabel("Value")
    set_q2cp_ticks(ax)
    plt.savefig("%s/Q.svg" % (savedir))

    # This plot can have multiple entries with the same index="N", so pivot fails.
    fig, ax = plt.subplots()
    for move in moves:
        tmp = bestdf[bestdf["sanmove"] == move]
        tmp.plot.line(x="N", y="Q", logx=True, logy=False, ax=ax)
    ax.legend(moves)
    plt.title("Value vs Child Node Visits")
    plt.xlabel("Child Node Visits")
    plt.ylabel("Value")
    set_q2cp_ticks(ax)
    plt.savefig("%s/Q2.svg" % (savedir))

    best.plot.bar(x="sanmove", y="P", legend=False)
    plt.xlabel("")
    plt.title("Policy")
    plt.savefig("%s/P.svg" % (savedir))
    plt.close("all")


def analyze_game(pgn_filename, gamenum, plynum, plies):
    try:
        # In case you have the data files already, but no lc0 exe.
        engine = chess.uci.popen_engine(LC0)
        info_handler = Lc0InfoHandler(None)
        engine.info_handlers.append(info_handler)
    except:
        print("Warning: Could not open Lc0 engine.")
        engine = None
        info_handler = None
    if not os.path.exists("plots"):
        os.makedirs("plots")
    outfile = open("plots/%s_%s_%0.3f_%s.html" % (pgn_filename, gamenum, (plynum+3)/2, plies), "w")
    outfile.write('<table width="%d" height="500">\n' % (plies*300))
    outfile.write("<tr>\n")
    for svgfile in ("board", "Q", "Q2", "N", "P"):
        for p in range(plies):
            savedir = "%s_%s_%05.1f" % (pgn_filename, gamenum, (plynum+p+3)/2.0)
            outfile.write('<td> <img src="%s/%s.svg" width="100%%"/> </td>\n' % (savedir, svgfile))
        outfile.write("</tr>\n")
    outfile.write("</tr>\n")
    outfile.write("</table>\n")
    outfile.close()
    for p in range(plies):
        analyze_and_plot(engine, info_handler, pgn_filename, gamenum, plynum+p)
    if engine: engine.quit()

def analyze_fen(name, fen):
    engine = chess.uci.popen_engine(LC0)
    info_handler = Lc0InfoHandler(None)
    engine.info_handlers.append(info_handler)
    analyze_and_plot(engine, info_handler, name, 0, 0, fen)
    engine.quit()

def compose(pgn_filename, gamenum, move_start, numplies, xsize=470, ysize=350, scale=0.6, scaleb=0.85):
    outfile = open("plots/%s_%s_%05.1f_%03d.html" % (pgn_filename, gamenum, move_start, numplies), "w")
    outfile.write('<table width="%d" height="500">\n' % (numplies*300))
    outfile.write("<tr>\n")
    for svgfile in ("board", "Q", "Q2", "N", "P"):
        for move in np.arange(move_start, move_start+numplies/2, 0.5):
            savedir = "%s_%s_%05.1f" % (pgn_filename, gamenum, move)
            outfile.write('<td> <img src="%s/%s.svg" width="100%%"/> </td>\n' % (savedir, svgfile))
        outfile.write("</tr>\n")
    outfile.write("</tr>\n")
    outfile.write("</table>\n")
    outfile.close()
    for move in np.arange(move_start, move_start+numplies/2, 0.5):
        savedir = "plots/%s_%s_%05.1f" % (pgn_filename, gamenum, move)
        fig = Figure(xsize*scale, ysize*5*scale,
            Panel(SVG("%s/board.svg" % (savedir)).scale(scale*scaleb)),
            Panel(SVG("%s/Q.svg"     % (savedir)).scale(scale)),
            Panel(SVG("%s/Q2.svg"    % (savedir)).scale(scale)),
            Panel(SVG("%s/N.svg"     % (savedir)).scale(scale)),
            Panel(SVG("%s/P.svg"     % (savedir)).scale(scale)),
        )
        fig.tile(1,5)
        fig.save("%s/all.svg" % (savedir))

    panels = []
    for move in np.arange(move_start, move_start+numplies/2, 0.5):
        panels.append(Panel(SVG("plots/%s_%s_%05.1f/all.svg" % (pgn_filename, gamenum, move))))
    fig = Figure(xsize*(numplies)*scale, ysize*5*scale, *panels)
    fig.tile(numplies, 1)
    filename = "plots/%s_%s_%05.1f_all" % (pgn_filename, gamenum, move_start)
    fig.save("%s.svg" % (filename))

    # cariosvg doesn't parse units "px"
    #cairosvg.svg2png(url="%s.svg" % (filename), write_to="%s.png" % (filename))

if __name__ == "__main__":
    usage_str = """
lc0_analyzer --pgn pgnfile --move 4.0 --numplies 6
lc0_analyzer --fen fenstring --numplies 6"""

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
    parser.add_argument("--lc0", type=str, required=True, help="lc0 executable")
    parser.add_argument("--w", type=str, required=True, help="path to weights")
    parser.add_argument("--nodes", type=int, default=2**16, help="number of nodes to analyze for each position, will be rounded to nearest power of 2")
    parser.add_argument("--topn", type=int, default=4, help="plot top N moves")
    parser.add_argument("--ply_per_page", type=int, default=6, help="how many plies to put together in one .svg page")

    args = parser.parse_args()

    LC0 = [
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
    NODES = [ 2**n for n in range(round(math.log(args.nodes))+1)]
    NUM_MOVES = args.topn

    if args.pgn:
        game = getgame(args.pgn, args.round)
        gamelen = len(game.end().board().move_stack)
        plynum = round(args.move*2-3)
        if plynum + args.numplies > gamelen:
            args.numplies = gamelen-plynum
        analyze_game(args.pgn, args.round, round(args.move*2-3), args.numplies)
        for m in np.arange(args.move, args.move+args.numplies/2, 0.5*args.ply_per_page):
            compose(args.pgn, args.round, m, min(args.ply_per_page, min(args.ply_per_page, args.numplies-(m-args.move)*2)))
    elif args.fen:
        analyze_fen(args.fen_desc, args.fen)
        #compose("plots/%s_%s" % (args.fen_desc, args.round), args.numplies)
    else: raise(Exception("must provide --pgn or --fen"))

