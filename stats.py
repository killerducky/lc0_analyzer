#!/usr/bin/env python3

def print_stats(stats):
    print("Games     : ", stats["TOTAL_GAMES"])
    print("Plies     : ", stats["TOTAL_PLIES"])
    print("Promotions: ", stats["TOTAL_PROMOTE"])
    print()
    print("L = promote left (queenside) legal")
    print("N = promote normal legal")
    print("R = promote right (kingside) legal")
    print("G = move made in game")
    print()
    print("Trivial:")
    print("%5s %5s %5s" % ("L", "N", "R"))
    for l in (False, True):
        for n in (False, True):
            for r in (False, True):
                if not sum ([l, n, r]) < 2: continue
                print("%5s %5s %5s %s %5s" % (l, n, r, "cases:", stats[(l,n,r)]))
    print()
    #print("Non-Trivial:")
    #print("%5s %5s %5s" % ("L", "N", "R"))
    #for l in (False, True):
    #    for n in (False, True):
    #        for r in (False, True):
    #            if sum ([l, n, r]) < 2: continue
    #            print("%5s %5s %5s %s %5s" % (l, n, r, "cases:", stats[(l,n,r)]))
    #print()

    print("%5s %5s %5s %s %5s" % ("L", "N", "R", "G", "%"))
    for l in (False, True):
        for n in (False, True):
            for r in (False, True):
                if sum ([l, n, r]) < 2: continue
                tot = stats[(l,n,r)]
                for game in ("L", "N", "R"):
                    percent = stats[(l,n,r,game)]
                    if percent > 0: percent = percent/tot * 100
                    print("%5s %5s %5s %s %5.1f (%5s/%5s)" % (l, n, r, game, percent, stats[(l,n,r,game)], stats[(l,n,r)]))
                print()

print ("="*80)
print("pgns-run1-20190111-0054 (40100)")
print ("="*80)
print_stats({'LEGAL_L': 1096, 'LEGAL_N': 39508, 'LEGAL_R': 1103, 'GAME_L': 914, 'GAME_N': 38322, 'GAME_R': 925, 'TOTAL_PROMOTE': 40161, 'TOTAL_PLIES': 16646893, 'TOTAL_GAMES': 158483, (False, False, False): 0, (False, False, False, 'L'): 0, (False, False, False, 'N'): 0, (False, False, False, 'R'): 0, (False, False, True): 259, (False, False, True, 'L'): 0, (False, False, True, 'N'): 0, (False, False, True, 'R'): 259, (False, True, False): 38107, (False, True, False, 'L'): 0, (False, True, False, 'N'): 38107, (False, True, False, 'R'): 0, (False, True, True): 699, (False, True, True, 'L'): 0, (False, True, True, 'N'): 99, (False, True, True, 'R'): 600, (True, False, False): 364, (True, False, False, 'L'): 364, (True, False, False, 'N'): 0, (True, False, False, 'R'): 0, (True, False, True): 30, (True, False, True, 'L'): 17, (True, False, True, 'N'): 0, (True, False, True, 'R'): 13, (True, True, False): 587, (True, True, False, 'L'): 472, (True, True, False, 'N'): 115, (True, True, False, 'R'): 0, (True, True, True): 115, (True, True, True, 'L'): 61, (True, True, True, 'N'): 1, (True, True, True, 'R'): 53})

print ("="*80)
print("pgns-run1-20190117-0054 (40300)")
print ("="*80)
print_stats({'LEGAL_L': 716, 'LEGAL_N': 27171, 'LEGAL_R': 693, 'GAME_L': 650, 'GAME_N': 26351, 'GAME_R': 611, 'TOTAL_PROMOTE': 27612, 'TOTAL_PLIES': 11411742, 'TOTAL_GAMES': 100853, (False, False, False): 0, (False, False, False, 'L'): 0, (False, False, False, 'N'): 0, (False, False, False, 'R'): 0, (False, False, True): 192, (False, False, True, 'L'): 0, (False, False, True, 'N'): 0, (False, False, True, 'R'): 192, (False, True, False): 26297, (False, True, False, 'L'): 0, (False, True, False, 'N'): 26297, (False, True, False, 'R'): 0, (False, True, True): 407, (False, True, True, 'L'): 0, (False, True, True, 'N'): 30, (False, True, True, 'R'): 377, (True, False, False): 234, (True, False, False, 'L'): 234, (True, False, False, 'N'): 0, (True, False, False, 'R'): 0, (True, False, True): 15, (True, False, True, 'L'): 11, (True, False, True, 'N'): 0, (True, False, True, 'R'): 4, (True, True, False): 388, (True, True, False, 'L'): 364, (True, True, False, 'N'): 24, (True, True, False, 'R'): 0, (True, True, True): 79, (True, True, True, 'L'): 41, (True, True, True, 'N'): 0, (True, True, True, 'R'): 38})

print ("="*80)
print("pgns-run1-20190128-0054 (40500)")
print ("="*80)
print_stats({'LEGAL_L': 1319, 'LEGAL_N': 39123, 'LEGAL_R': 1512, 'GAME_L': 1183, 'GAME_N': 37367, 'GAME_R': 1414, 'TOTAL_PROMOTE': 39964, 'TOTAL_PLIES': 18186077, 'TOTAL_GAMES': 158563, (False, False, False): 0, (False, False, False, 'L'): 0, (False, False, False, 'N'): 0, (False, False, False, 'R'): 0, (False, False, True): 371, (False, False, True, 'L'): 0, (False, False, True, 'N'): 0, (False, False, True, 'R'): 371, (False, True, False): 37319, (False, True, False, 'L'): 0, (False, True, False, 'N'): 37319, (False, True, False, 'R'): 0, (False, True, True): 955, (False, True, True, 'L'): 0, (False, True, True, 'N'): 25, (False, True, True, 'R'): 930, (True, False, False): 433, (True, False, False, 'L'): 433, (True, False, False, 'N'): 0, (True, False, False, 'R'): 0, (True, False, True): 37, (True, False, True, 'L'): 18, (True, False, True, 'N'): 0, (True, False, True, 'R'): 19, (True, True, False): 700, (True, True, False, 'L'): 677, (True, True, False, 'N'): 23, (True, True, False, 'R'): 0, (True, True, True): 149, (True, True, True, 'L'): 55, (True, True, True, 'N'): 0, (True, True, True, 'R'): 94})

print ("="*80)
print ("pgns-run1-20190306-1254.tar.bz2 (41369)")
print ("="*80)
print_stats({'LEGAL_L': 2359, 'LEGAL_N': 53304, 'LEGAL_R': 2343, 'GAME_L': 2042, 'GAME_N': 50361, 'GAME_R': 2238, 'TOTAL_PROMOTE': 54641, 'TOTAL_PLIES': 24424424, 'TOTAL_GAMES': 209418, (False, False, False): 0, (False, False, False, 'L'): 0, (False, False, False, 'N'): 0, (False, False, False, 'R'): 0, (False, False, True): 539, (False, False, True, 'L'): 0, (False, False, True, 'N'): 0, (False, False, True, 'R'): 539, (False, True, False): 50269, (False, True, False, 'L'): 0, (False, True, False, 'N'): 50269, (False, True, False, 'R'): 0, (False, True, True): 1474, (False, True, True, 'L'): 0, (False, True, True, 'N'): 53, (False, True, True, 'R'): 1421, (True, False, False): 742, (True, False, False, 'L'): 742, (True, False, False, 'N'): 0, (True, False, False, 'R'): 0, (True, False, True): 56, (True, False, True, 'L'): 7, (True, False, True, 'N'): 0, (True, False, True, 'R'): 49, (True, True, False): 1287, (True, True, False, 'L'): 1249, (True, True, False, 'N'): 38, (True, True, False, 'R'): 0, (True, True, True): 274, (True, True, True, 'L'): 44, (True, True, True, 'N'): 1, (True, True, True, 'R'): 229})

print ("="*80)
print ("pgns-run2-20190128-0054.tar.bz2 (32930)")
print ("="*80)
print_stats({'LEGAL_L': 1550, 'LEGAL_N': 38472, 'LEGAL_R': 1410, 'GAME_L': 1320, 'GAME_N': 36816, 'GAME_R': 1114, 'TOTAL_PROMOTE': 39250, 'TOTAL_PLIES': 15575689, 'TOTAL_GAMES': 125167, (False, False, False): 0, (False, False, False, 'L'): 0, (False, False, False, 'N'): 0, (False, False, False, 'R'): 0, (False, False, True): 270, (False, False, True, 'L'): 0, (False, False, True, 'N'): 0, (False, False, True, 'R'): 270, (False, True, False): 36506, (False, True, False, 'L'): 0, (False, True, False, 'N'): 36506, (False, True, False, 'R'): 0, (False, True, True): 924, (False, True, True, 'L'): 0, (False, True, True, 'N'): 159, (False, True, True, 'R'): 765, (True, False, False): 462, (True, False, False, 'L'): 462, (True, False, False, 'N'): 0, (True, False, False, 'R'): 0, (True, False, True): 46, (True, False, True, 'L'): 28, (True, False, True, 'N'): 0, (True, False, True, 'R'): 18, (True, True, False): 872, (True, True, False, 'L'): 722, (True, True, False, 'N'): 150, (True, True, False, 'R'): 0, (True, True, True): 170, (True, True, True, 'L'): 108, (True, True, True, 'N'): 1, (True, True, True, 'R'): 61})

print ("="*80)
print ("pgns-run2-20190307-1254 (50381)")
print ("="*80)
print_stats({'LEGAL_L': 6182, 'LEGAL_N': 120105, 'LEGAL_R': 5534, 'GAME_L': 4417, 'GAME_N': 114861, 'GAME_R': 4230, 'TOTAL_PROMOTE': 123508, 'TOTAL_PLIES': 41370749, 'TOTAL_GAMES': 400510, (False, False, False): 0, (False, False, False, 'L'): 0, (False, False, False, 'N'): 0, (False, False, False, 'R'): 0, (False, False, True): 1442, (False, False, True, 'L'): 0, (False, False, True, 'N'): 0, (False, False, True, 'R'): 1442, (False, True, False): 112949, (False, True, False, 'L'): 0, (False, True, False, 'N'): 112949, (False, True, False, 'R'): 0, (False, True, True): 2935, (False, True, True, 'L'): 0, (False, True, True, 'N'): 798, (False, True, True, 'R'): 2137, (True, False, False): 1742, (True, False, False, 'L'): 1742, (True, False, False, 'N'): 0, (True, False, False, 'R'): 0, (True, False, True): 219, (True, False, True, 'L'): 89, (True, False, True, 'N'): 0, (True, False, True, 'R'): 130, (True, True, False): 3283, (True, True, False, 'L'): 2253, (True, True, False, 'N'): 1030, (True, True, False, 'R'): 0, (True, True, True): 938, (True, True, True, 'L'): 333, (True, True, True, 'N'): 84, (True, True, True, 'R'): 521})

