#!/bin/bash
WEIGHT=32194
NODES=65536

LC0="./lc0_analyzer.py \
--lc0=/mnt/c/Users/Andy/Desktop/arena_3.5.1/Engines/lc0-v0.20.1-windows-cuda/lc0.exe \
--w=c:/Users/Andy/Downloads/$WEIGHT \
--nodes=$NODES
"

#$LC0 --pgn="mattblachess_Bh6+.pgn"      --move=19.5 --numplies=6   # After 19. Ng4, Black tries 19...Bc6 to attack queen, misses a deflection later
#$LC0 --pgn=TCEC14_divp.pgn --round=28.4 --move=33.5 --numplies=10  # SF > Lc0  Black plays 33...Qxf4

#$Lc0 --fen_desc="test"      --fen="r1r2n2/1p2k2p/p3p2P/3b2B1/3P4/3B4/P6K/2R1R3 b - - 0 31"
#$Lc0 --fen_desc="sf_lc0_m3" --fen="8/5p1k/5q2/1p4R1/4n2P/P5PK/4Q3/2q5 w - - 0 74"
$LC0 --fen_desc="lc0_fire"  --fen="r1bqk2r/1p2bppp/p1nppn2/8/3NP3/2N1B3/PPPQBPPP/R3K2R w KQkq - 2 9"

