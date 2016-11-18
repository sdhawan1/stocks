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

#start out by retrieving data for one stock and running some tests on it.
f = open("data/aapl_2yrs.csv")
aapl = list(csv.reader(f))
colnames = aapl[0]
aapl = aapl[2:]


#if we were to use a markov model, we would invest when we thought the price was
#  likely to increase, and we would sell when we thought it was likely to decrease.





