#!/usr/bin/env python3

import svgutils.transform as sg
from svgutils.compose import *
import sys
import math

outplot = sys.argv[1]
inplots = sys.argv[2:]

xsize = 0
ysize = 0
scale = 1.0


fig = None
for i, plot in enumerate(inplots):
    x = i % 2
    y = i // 2
    tmpfig = sg.fromfile(plot)
    xsize = float(tmpfig.width[:-2])   # chop "pt" off
    ysize = float(tmpfig.height[:-2])
    if not fig: fig = sg.SVGFigure(xsize*2*scale, math.ceil(len(inplots)/2)*ysize*scale)
    tmpplot = tmpfig.getroot()
    tmpplot.moveto(x*xsize, y*ysize)
    fig.append(tmpplot)

fig.save(outplot)

