lc0_analyzer.py takes pgn files or FEN strings, analyzes them with the Lc0 chess engine, and outputs some graphs to visualize Lc0's search. For each position, several graphs are created (right click open image in new tab to zoom in more). 

<img src="plots/mattblachess_Bh6+.pgn_None_019.5_all.svg"/>

* Value vs Total Nodes - Shows how the value of the moves change over time (Total Nodes searched).
* Value vs Child Node Visits - Show how the value of the top moves change, but assuming equal time (Child Node Visits) is given to each candidate move.
* Child Node Visits vs Total Nodes - Shows how much total time (visits) each move is searched.
* Policy - Output of Lc0's NN Policy head.

Some highlights from the giant example above:

<img src="plots/plots/mattblachess_Bh6+.pgn_None_019.5/board.svg" width="200"/>

Black to play, Lc0 doesn't realize Bc6 is a losing move. To see the problem, let's look at the position a few moves later with White to play:

<img src="plots/mattblachess_Bh6+.pgn_None_022.0/board.svg" width="200"/>

<img src="plots/mattblachess_Bh6+.pgn_None_022.0/Q.svg" width="400"/>

After 1K nodes, Lc0 realizes Bg7+ wins.

<img src="plots/mattblachess_Bh6+.pgn_None_022.0/Q2.svg" width="400"/>

This graph shows Lc0 knows Bg7+ is winning the moment is starts searching it.

<img src="plots/mattblachess_Bh6+.pgn_None_022.0/N.svg" width="400"/>

Once Lc0 finds the winning Bg7+, it quickly gets all the search time.

<img src="plots/mattblachess_Bh6+.pgn_None_022.0/P.svg" width="400"/>

The problem is Bg7+ has low Policy, so the search ignores it for a long time.


