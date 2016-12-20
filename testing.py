
#test the "stockhmm" function using cross validation.

#the problem with this test so far: there isn't a diverse enough set of 
#  training / testdata. This results in uniformly low or high scores.

import csv
from stockhmm_flexibledist_permutations import stockhmm


#this function should run the model and return a score
def runmodel_score(trdata, testdata):
	#now, train our model. Smoothness and visibility are 3, and money is 1000
	h = stockhmm(3, 3, trdata, 1000)

	#test our model by calling "predict" with the trained hmm on the test data.
	money = h.predict_testdataset(testdata)

	#open file & compile a list of investment values and stock closing prices.
	f = open('out.txt')
	farr = f.read().split("\n")
	modelvals=[]
	stockvals=[]
	for l in farr:
		larr = l.split(" ")
		modelvals += [float(larr[2])]
		stockvals += [float(larr[3])]
		
	#scale up the stockvals
	s0 = stockvals[0]
	m0=modelvals[0]
	stockvals = [s*m0/s0 for s in stockvals]
	#one metric is to count the days where the model is ahead:
	modelaheadpoints = [(modelvals[i] > stockvals[i]) for i in range(len(modelvals))]
	modelahead = sum(modelaheadpoints) / float(len(modelvals))
	#another metric is to take an integral: sum the difference between the model and reality:
	modelintegral = sum( [modelvals[i] - stockvals[i] for i in range(len(modelvals))] ) / len(modelvals)
	
	#also compute the opening and closing of passive investment & stockhmm
	print "stockopen: %f, stockclose: %f, modelopen: 1000.0, modelclose: %f" %(stockvals[0], stockvals[-1], modelvals[-1])
	return [modelahead, modelintegral]

#set the number of "folds"
folds=5
	
#get the training data
symbol = "dja"
datapath = "data/DJA.csv"
f = open(datapath)
stock = list(csv.reader(f))
stock = stock[4:]
stock = [float(s[1]) for s in stock]
#set the number of test iterations, based on #folds.
itersize=len(stock)/folds

#for each iteration, call the 'runmodel' function.
scores=[]
aheadscores=[]
integralscores=[]
i=0
j=0
for ind0 in range(folds-1):
	#choose a slice of the trdata to be testdata.
	j = i+itersize
	testdata = stock[i:j]
	trdata = stock[:i]+stock[j:]
	scorevals = runmodel_score(trdata, testdata)
	aheadscores += [scorevals[0]]
	integralscores += [scorevals[1]]
	print "%d, %d, %d" %(i, j, itersize)
	i=j
	print scorevals
print "Avg. time ahead:"
print sum(aheadscores)/len(aheadscores)
print "Avg. amount ahead:"
print sum(integralscores)/len(integralscores)

#get the test data
"""
symbol = "ea"
datapath = "data/%s_10yrs.csv"%symbol
f = open(datapath)
stock = list(csv.reader(f))
stock = stock[2:]
testdata = [float(a[1]) for a in stock]
"""

#findings with the current test: it performs very badly over the long term. [I have to redo 5 / 10 crossval.]
#  trying out shorter term investments...

# Scores: ratio of times performing better than the market:
# 5-crossval: 0.13
# 10-crossval: 0.232
# 100-crossval: 0.37.

#Scores: average amount ahead of the market:
# 5-crossval: -766.23 (this is also really bad, the market is 70% better than my model on avg.)
# 10-crossval: -415.812 (this is atrocious - the market is 50% ahead of my model!)
# 100-crossval: -35.35 (out of 1000, this isn't too bad. Only about 3% under the model.)


