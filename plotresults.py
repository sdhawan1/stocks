
#In this file, create plots to document the performance of the stock metrics.

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

#also create a function to plot the growth of one single stock.

#plot the results of doing a calculation of "runstockhmm."
def plotresults(symbol, outfilepath):

	#open file with the output
	f = open(outfilepath)
	farr = f.read().split("\n")

	#compile a list of investment values and stock closing prices.
	modelvals=[]
	stockvals=[]
	for l in farr:
		larr = l.split(" ")
		modelvals += [float(larr[2])]
		stockvals += [float(larr[3])]

	#scale up the stock values
	initstockval = stockvals[0]
	stockvals = [s * modelvals[0]/initstockval for s in stockvals]
	x = range(len(stockvals))

	#finally, plot.
	#first, create a figure title.
	fig = plt.figure()
	fig.suptitle('Growth of Stockhmm vs. %s stock' % symbol)
	#next, create axis labels:
	ax = fig.add_subplot(111)
	fig.subplots_adjust(top=0.85)
	ax.set_title('Theoretical Growth of $1000 over time with stockhmm')
	ax.set_xlabel('Elapsed Days')
	ax.set_ylabel('Dollar Value of Investment')
	#finally, create two line graphs + legend.
	ax.plot(x, stockvals, label="passive investment")
	ax.plot(x, modelvals, label="stockhmm model")
	ax.legend()

	plt.show()

#run the above function
"""
symbol = 'INTC'
outfilepath = 'out_%s.txt'%symbol
plotresults(symbol, outfilepath)
"""
