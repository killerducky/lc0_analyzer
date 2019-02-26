#!/usr/bin/env python3

#
#

import re
import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd
import os
import sys
import math
import time
import argparse
import datetime
import threading
import queue
import subprocess


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
    (_, _, N, _, P, Q, D, U, Q_U, V, _) = floats
    move_infos = {}
    move_infos["TN"] = int(TN)
    move_infos["sanmove"] = sanmove
    move_infos["ucimove"] = ucimove
    move_infos["N"] = int(N)
    move_infos["P"] = float(P)
    move_infos["Q"] = float(Q)
    move_infos["U"] = float(U)
    move_infos["D"] = float(U)
    if V == "-.----": V = 0
    move_infos["V"] = float(V)
    return move_infos

prevtime = datetime.datetime.now() - datetime.timedelta(seconds=999)
def plot(df):
    global prevtime
    thistime = datetime.datetime.now()
    difftime = thistime - prevtime
    prevtime = thistime
    if difftime.total_seconds() < 1:
        return
    if not plt.fignum_exists(1):
        fig, ax = plt.subplots(2, 2)
        fig.set_size_inches(12, 8)
    else:
        fig = plt.figure(1)
        fig.clf()
        fig.add_subplot(221)
        fig.add_subplot(222)
        fig.add_subplot(223)
        fig.add_subplot(224)
    fig = plt.figure(1)
    ax = fig.get_axes()

    # Filter top moves, and get P
    TNmax = df["TN"].max()
    best = df[df["TN"] == TNmax].sort_values("N", ascending=False).head(NUM_MOVES)
    moves = list(best["sanmove"])
    bestdf = df.loc[df["sanmove"].isin(moves)]
    #print(bestdf)

    plt.ion()

    # Plots
    fig = plt.figure(1)
    ax = fig.get_axes()[2]
    plt.axes(ax)
    for move in moves:
        tmp = bestdf[bestdf["sanmove"] == move]
        tmp.plot.line(x="TN", y="N", logx=True, logy=True, ax=ax)
    ax.legend(moves)
    plt.title("Child Node Visits vs Total Nodes")
    plt.xlabel("Total Nodes")
    plt.ylabel("Child Nodes")

    fig = plt.figure(1)
    ax = fig.get_axes()[0]
    plt.axes(ax)
    for move in moves:
        tmp = bestdf[bestdf["sanmove"] == move]
        tmp.plot.line(x="TN", y="Q", logx=True, logy=False, ax=ax)
    ax.legend(moves)
    plt.title("Value vs Total Nodes")
    plt.xlabel("Total Nodes")
    plt.ylabel("Value")
    set_q2cp_ticks(ax)

    # This plot can have multiple entries with the same index="N", so pivot fails.
    fig = plt.figure(1)
    ax = fig.get_axes()[1]
    plt.axes(ax)
    for move in moves:
        tmp = bestdf[bestdf["sanmove"] == move]
        tmp.plot.line(x="N", y="Q", logx=True, logy=False, ax=ax)
    ax.legend(moves)
    plt.title("Value vs Child Node Visits")
    plt.xlabel("Child Node Visits")
    plt.ylabel("Value")
    set_q2cp_ticks(ax)

    fig = plt.figure(1)
    ax = fig.get_axes()[3]
    plt.axes(ax)
    best.plot.bar(x="sanmove", y="P", legend=False, ax=ax)
    plt.xlabel("")
    plt.title("Policy")
    plt.tight_layout()
    plt.show()
    plt.pause(0.001)

class UciWrite(threading.Thread):
    def __init__(self, p, q):
        threading.Thread.__init__(self)
        self.p = p
        self.q = q
    def run(self):
        # Secretly set the hidden option for user
        p.stdin.write("setoption name LogLiveStats value true\n")
        while 1:
            s = sys.stdin.readline()
            p.stdin.write(s)
            p.stdin.flush()
            if s.startswith("position"):
                q.put(s)
            if s.startswith("quit"):
                return

class UciRead(threading.Thread):
    def __init__(self, p, q):
        threading.Thread.__init__(self)
        self.p = p
        self.q = q
        self.reset()
    def reset(self):
        self.strings = []
        self.totalnodes = None
        self.position = None
    def run(self):
        while p.poll() == None:
            if not self.q.empty():
                sys.stdout.flush()
                self.reset()
                self.position = q.get()
                # TODO: Parse position so we can have SAN notation moves
            info = p.stdout.readline().rstrip()
            print(info)
            sys.stdout.flush()
            if info.startswith("info string"):
                # "info string c7f4  (268 ) N:      40 (+37) (P: 20.23%) (Q: -0.04164) (U: 0.08339) (Q+U:  0.04175) (V:  0.1052)"
                (_1, _2, move, info) = info.split(maxsplit=3)
                s = "TN: %d %6s %s %s" % (self.totalnodes, move, move, info)
                self.strings.append(s)
            elif info.startswith("info depth"):
                # info depth 1 seldepth 2 time 14 nodes 3 score cp 57 hashfull 0 nps 214 tbhits 0 multipv 1 pv e2e4 e7e5
                m = re.search("nodes (\d+)", info)
                if not m: raise
                totalnodes = int(m.group(1))
                if self.totalnodes != totalnodes:
                    self.totalnodes = totalnodes
                    if len(self.strings) > 1:
                        move_infos = []
                        for line in self.strings:
                            line = "INFO: " + line
                            info = parse_info(line)
                            move_infos.append(info)
                        df = pd.DataFrame(move_infos)
                        plot(df)

if __name__ == "__main__":
    usage_str = """
TBD"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage_str)
    parser.add_argument("--lc0", type=str, required=True, help="lc0 executable")
    parser.add_argument("--topn", type=int, default=4, help="plot top N moves")

    args = parser.parse_args()

    LC0 = [
        args.lc0,
    ]
    NUM_MOVES = args.topn

    p = subprocess.Popen(LC0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    q = queue.Queue()
    uciRead = UciRead(p, q)
    uciWrite = UciWrite(p, q)
    uciRead.start()
    uciWrite.start()
    uciWrite.join()

