#!/usr/bin/env python3

#
# Usage:
#
# Modify the global variables at top, and the analyze calls at the very bottom
# Then just run with no arguments
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
from collections import OrderedDict

LC0 = [
    #"/home/aolsen/bin/lc0-v0.20.1",
    #"/mnt/c/Users/Andy/Desktop/arena_3.5.1/Engines/lc0-v0.19.0-windows-cuda/lc0.exe",
    "/mnt/c/Users/Andy/Desktop/arena_3.5.1/Engines/lc0-v0.20.1-windows-cuda/lc0.exe",
    #"-w", "/home/aolsen/lcnetworks/32194",
    "-w", "c:/Users/Andy/Downloads/32194",
    #"-w", "c:/Users/Andy/Downloads/40150",
    #"-w", "c:/Users/Andy/Downloads/40196",
    "-l", "lc0log.txt",
    #"-t", "1",
    #"--max-prefetch=0",
    #"--no-out-of-order-eval",   # Otherwise nncache messes things up?  See issue #680
    #"--collision-visit-limit=1",
    #"--minibatch-size=1",
    "--minibatch-size=16",      # because of #680, use this compromise between accuracy and speed
    "--smart-pruning-factor=0", # We will start and stop in loops, so disable pruning
    "--nncache=1000000",
    "--verbose-move-stats",
]
NODES = [ 2**n for n in range(20+1) ]    # 2**20 = 1M
#NODES = [ 2**n for n in range(16+1) ]   # 2**16 = 64K
#NODES = [ 2**n for n in range(4+1) ]

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
def analyze(engine, info_handler, pgn_filename, gamenum, plynum, fen=None):
    savedir = "plots/%s_%s_%s" % (pgn_filename, gamenum, plynum)
    datafilename = "%s/data.html" % (savedir)
    if not os.path.exists(datafilename):
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        outfile = open(datafilename, "w")
        outfile.write("""
<img src="board.svg" height="100%"/> <br>
<img src="Q.svg"/> <br>
<img src="Q2.svg"/> <br>
<img src="N.svg"/> <br>
<img src="P.svg"/> <br>
<pre>
        """)
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
    plot(pgn_filename, gamenum, plynum)

def plot(pgn_filename, gamenum, plynum):
    savedir = "plots/%s_%s_%s" % (pgn_filename, gamenum, plynum)

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
    tmp = bestdf.pivot(index="TN", columns="sanmove", values="N")
    ax = tmp.plot.line(logx=True, logy=True)
    ax.legend(moves)
    plt.title("Child Node Visits vs Total Nodes")
    plt.xlabel("Total Nodes")
    plt.ylabel("Child Nodes")
    plt.savefig("%s/N.svg" % (savedir))


    tmp = bestdf.pivot(index="TN", columns="sanmove", values="Q")
    ax = tmp.plot.line(logx=True, logy=False)
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
        engine = chess.uci.popen_engine(LC0)
        info_handler = Lc0InfoHandler(None)
        engine.info_handlers.append(info_handler)
    except: 
        print("Warning: Could not open Lc0 engine.")
        engine = None
        info_handler = None
    if not os.path.exists("plots"):
        os.makedirs("plots")
    outfile = open("plots/%s_%s_%s_%s.html" % (pgn_filename, gamenum, plynum, plies), "w")
    outfile.write('<table width="%d" height="500">\n' % (plies*300))
    outfile.write("<tr>\n")
    for svgfile in ("board", "Q2", "N", "P", "Q"):
        for p in range(plies):
            savedir = "%s_%s_%s" % (pgn_filename, gamenum, plynum+p)
            outfile.write('<td> <img src="%s/%s.svg" width="100%%"/> </td>\n' % (savedir, svgfile))
        outfile.write("</tr>\n")
    outfile.write("</tr>\n")
    outfile.write("</table>\n")
    outfile.close()
    for p in range(plies):
        analyze(engine, info_handler, pgn_filename, gamenum, plynum+p)   # SF > Lc0
    if engine: engine.quit()

#analyze_game("tcec_14_divp.pgn", "28.4", 2*(33-1)+0, 10)   # SF > Lc0
#analyze_game("CCC_Be4_SF10_Lc0.pgn", "20", 2*(71-1)+0, 8)   # Black Lc0 deflects to promote, misses counter tactic
analyze_game("mattblachess_Bh6+.pgn", None, 2*(19-1)+0, 6)   # Black Lc0 deflects to promote, misses counter tactic

def analyze_fen(name, fen):
    engine = chess.uci.popen_engine(LC0)
    info_handler = Lc0InfoHandler(None)
    engine.info_handlers.append(info_handler)
    analyze(engine, info_handler, name, 0, 0, fen)
    engine.quit()

#analyze_fen("test", "r1r2n2/1p2k2p/p3p2P/3b2B1/3P4/3B4/P6K/2R1R3 b - - 0 31")
#analyze_fen("lc0_fire", "r1bqk2r/1p2bppp/p1nppn2/8/3NP3/2N1B3/PPPQBPPP/R3K2R w KQkq - 2 9")
#analyze_fen("sf_lc0_m3", "8/5p1k/5q2/1p4R1/4n2P/P5PK/4Q3/2q5 w - - 0 74")
