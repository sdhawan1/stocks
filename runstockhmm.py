#do one run through of the stockhmm function, and plot the results.
## TAKE THE STOCK SYMBOL FROM THE USER!

from stockhmm_flexibledist import *
from plotresults import plotresults

#start out by retrieving data for one stock and training it.
"""
symbol = "aapl"
datapath = "data/%s_10yrs.csv"%symbol
f = open(datapath)
stock = list(csv.reader(f))
stock = stock[2:]
trdata = [float(a[1]) for a in stock[:-500]]

#figure out the testdata:
symbol = "aapl"
datapath = "data/%s_10yrs.csv"%symbol
f = open(datapath)
stock = list(csv.reader(f))
stock = stock[2:]
testdata = [float(a[1]) for a in stock[-500:]]
"""


#retrieve data from Dow Jones IA, use it to train & test.
# NOTE: RETRIEVED DJA DATA FROM https://measuringworth.com/DJA/result.php
symbol="dja"
f=open("data/DJA.csv")
stock = list(csv.reader(f))
stock = stock[4:]
trdata = [float(a[1]) for a in stock[:15000]]
testdata = [float(a[1]) for a in stock[15000:]]



#now, train our model. Smoothness and visibility are 2 or 3, and money is 1000
h = stockhmm(6, 2, trdata, 1000)

#test our model by calling "predict" with the trained hmm on the test data.
#DEBUGGING: MAKE THE TEST DATA MORE MANAGEABLE:
#testdata = testdata[:365]
money = h.predict_testdataset(testdata)

#An additional test: measure how many times the HMM was "right"
#  [note: this test is best with a linear util0.]
#precision: measure how many times we invested and gained.
fout = open("out.txt")
results = fout.read().split('\n')
results2 = [r.split(' ') for r in results]
stockprices = [float(r[-1]) for r in results2]
investments = [float(r[1][:-1]) for r in results2]
modelpos=0
modeltruepos=0
modelfalsepos=0
modelneg=0
modeltrueneg=0
modelfalseneg=0
for i in range(1, len(investments)):
	if investments[i] > 0.1:
		modelpos+=1
		if stockprices[i] > stockprices[i-1]:
			modeltruepos += 1
		else:
			modelfalseneg += 1
	else:
		modelneg+=1 
		if stockprices[i] < stockprices[i-1]:
			modeltrueneg += 1
		else:
			modelfalsepos += 1

#recall: of all the times the reality was actually "positive", how many times did we guess "positive"?
#precision: of all the times the model said "positive", how many were actually positive?
print ""
print "end balance: %f" % money
print "start: %f" % testdata[0],
print "end: %f" % testdata[-1]
print "recall of positives: %f" % (float(modeltruepos)/modelpos)
print "precision of positives: %f" % (float(modeltruepos)/(modeltruepos+modelfalseneg) )
print "recall of negatives: %f" % (float(modeltrueneg)/modelneg)
print "precision of negatives: %f" % (float(modeltrueneg)/(modeltrueneg+modelfalsepos) )

#call the plot function to measure these results:
plotresults(symbol.upper(), "out.txt")