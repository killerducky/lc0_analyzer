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
import re
import matplotlib.pyplot as plt
import matplotlib.axes
import pandas as pd
import numpy as np

df2 = pd.DataFrame()
#row = {"k":"1", "a":0}
#df2 = df2.append(row, ignore_index=True)
#row = {"k":"2", "a":3}
#df2 = df2.append(row, ignore_index=True)
#print(df2)

with open("tcec14_sufi.pgn") as pgn:
    while True:
        game = chess.pgn.read_game(pgn)
        if not game:
            break
        df = []
        df2 = pd.DataFrame()
        print(game.headers["Round"], game.headers["White"], game.headers["Black"], game.headers["Result"])
        for node in game.mainline():
            df.append({})
            board = node.board()
            row = {}
            row["Round"] = game.headers["Round"]
            row["sanmove"] = node.san()
            if board.turn:
                row["movenum"] = board.fullmove_number-1
                row["whomoved"] = "b"
            else:
                row["movenum"] = board.fullmove_number
                row["whomoved"] = "w"
            if node.comment.startswith("book"):
                df[-1]["wv"] = "0.0"
            else:
                for item in node.comment.split(","):
                    if item == "": continue
                    k, _, v = item.partition("=")
                    k = re.sub(" ", "", k)
                    df[-1][k] = v
                    row[k] = v
            if df[-1]["wv"].startswith("-M"): df[-1]["wv"] = -999
            elif df[-1]["wv"].startswith("M"): df[-1]["wv"] = 999
            df[-1]["wv"] = float(df[-1]["wv"])
            row["wv"] = df[-1]["wv"]
            if not board.turn:
                #print("%3s. %5s %5.2f" % (len(df)//2+1, node.san(), df[-1]["wv"]), end="")
                print("%3s. %5s %5.2f" % (board.fullmove_number, node.san(), df[-1]["wv"]), end="")
            else:
                print("  %5s %5.2f" % (node.san(), df[-1]["wv"]), end="")
                if len(df) > 2:
                    if abs(df[-1]["wv"] - df[-3]["wv"]) > 0.5: print(" black moob/boom", end="")
                    if abs(df[-2]["wv"] - df[-4]["wv"]) > 0.5: print(" white moob/boom", end="")
                print()
            df2 = df2.append(row, ignore_index=True)
        print()
        print(df2)
        fig, ax = plt.subplots()
        for color in ("w", "b"):
            tmp = df2[df2["whomoved"] == color]
            tmp.plot.line(x="movenum", y="wv", ax=ax)
        ax.legend("w", "b")
        ax.set_ylim(-10, 10)
        plt.savefig("tcec_14_sufi_round_%s.svg" % (game.headers["Round"].rjust(4, "0")))
        plt.close("all")
