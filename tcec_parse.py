#!/usr/bin/env python3

# wget https://tcec.chessdom.com/json/event.pgn

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
import sqlite3

with open("tcec14_sufi.pgn") as pgn:
    while True:
        game = chess.pgn.read_game(pgn)
        if not game:
            break
        df2 = pd.DataFrame()
        print(game.headers["Round"], game.headers["White"], game.headers["Black"], game.headers["Result"])
        for node in game.mainline():
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
                row["wv"] = "0.0"
            else:
                for item in node.comment.split(","):
                    if item == "": continue
                    k, _, v = item.partition("=")
                    k = re.sub(" ", "", k)
                    row[k] = v
            if row["wv"].startswith("-M"): row["wv"] = -999
            elif row["wv"].startswith("M"): row["wv"] = 999
            row["wv"] = float(row["wv"])
            df2 = df2.append(row, ignore_index=True)
            if not board.turn:
                print("%3s. %5s %5.2f" % (board.fullmove_number, node.san(), row["wv"]), end="")
            else:
                print("  %5s %5.2f" % (node.san(), row["wv"]), end="")
                if row["movenum"] > 1:
                    if abs(df2.iloc[-1]["wv"] - df2.iloc[-3]["wv"]) > 0.5: print(" black moob/boom", end="")
                    if abs(df2.iloc[-2]["wv"] - df2.iloc[-4]["wv"]) > 0.5: print(" white moob/boom", end="")
                print()
        print()
        print(df2)
        fig, ax = plt.subplots()
        for color in ("w", "b"):
            tmp = df2[df2["whomoved"] == color]
            tmp.plot.line(x="movenum", y="wv", ax=ax)
        ax.legend(["w", "b"])
        ax.set_ylim(-5, 5)
        plt.savefig("tcec_14_sufi_round_%s.svg" % (game.headers["Round"].rjust(4, "0")))
        plt.close("all")
        #conn = sqlite3.connect("games.db")
        #df2.to_sql("games", conn)
        #break

#conn = sqlite3.connect("games.db")
##cur = conn.cursor()
##df2 = cur.execute("select * from games").fetchall()
#df2 = pd.read_sql_query("select * from games;", conn)
#print(df2)
#raise

