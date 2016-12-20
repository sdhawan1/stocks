#Here, I will try to create a model to help me figure out what stocks to invest in.

### The data ###
#  I have accumulated data for several tech stocks; the data is about two years long.
#    data comes from the site: www.nasdaq.com/symbol.

### The goal ###
#  My goal is to predict, based on the past several months of the stock's performance,
#   which combination of stocks will maximize my profits in the next few months.
#   this can be written like a probabilistic prediction algorithm. It can start out
#   as a simple variant of the "cat and mouse" problem from AI.


import numpy
import csv
from plotresults import plotresults

#try to call the "plotresults" file.
plotresults("T", "out.txt")