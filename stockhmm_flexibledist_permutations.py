
## Create an hmm model for the purpose of making investment decisions.

#Current findings: the algorithm has very high performance. It makes dramatic
#   gains in stock price, even over periods where the stock it's tracking went down.
#Next steps: perform more testing & adjust the algorithm. Also add to write up (talk about k-fold crossval).
#  change the algorithm so that the order of state changes matters.
#  change the algorithm's "util0" function and perform more tests.

import numpy
import csv
import math
from plotresults import plotresults
from utilfn0 import calcutil0

class stockhmm(object):
	m = 0
	s = 0
	v = 0
	sd = 0
	statemap = {}
	stdivs = []
	avgstatechange = []
	#FIGURE OUT HOW TO ADD FUNCTION "UTILFN"

	#initially, we should set "trdata" equal to a full list of closing prices only.
	#"utilfn" = the utility function we want for our data [INCLUDE THIS LATER].
	def __init__(self, smoothness, visibility, trdata, money):
		#input basic tests after I learn exception handling

		#take the training data and fill out our HMM. Every training input (sorted)
		# should map to a set of probabilities, each corresponding to how likely
		# the next state is.
		self.m = money
		self.s = smoothness
		self.v = visibility
		self.statemap = {}
		self.stdivs = []
		self.avgstatechange = []

		#"smooth" the trdata so that there are 1/s the number of original inputs;
		#  let every s closing values be averaged to create a new one in a modified list.
		moddata = []
		for i in range(self.s, len(trdata), self.s):
			nextval = numpy.mean(trdata[i-self.s: i])
			moddata += [nextval]
		trdata = moddata
		
		#===========================================================================#
		### WARNING: THIS MAY BE A FORM OF OVERFITTING! [TR DISTRIBUTION != TEST DIST.]
		#Create an alternate method to compute zscoretrdata, which we know will be equitable,
		# in spite of the specific distribution of the training data.
		altzstrdata = self.altstatecalc(trdata)
		#also create an expected change variable for every state:
		self.computeexpectedchange(trdata)
		
		#print "\naltzstrdata:"
		#print "0: %d, 1: %d, 2: %d, 3: %d, 4: %d, 5: %d, 6: %d\n" % (altzstrdata.count(0), altzstrdata.count(1), altzstrdata.count(2),
		#	altzstrdata.count(3), altzstrdata.count(4), altzstrdata.count(5), altzstrdata.count(6))
		
		
		#the statemap's input should be every possible combination of five states
		#iterate through the training data and store data in the statemap
		# NOTE: WE DO NOT SORT THE INPUTS HERE - WANT TO TRY PERMUTATIONS FOR MORE ACCURACY.
		for i in range(self.v, len(altzstrdata)):
			state = altzstrdata[i]
			input0 = altzstrdata[i-self.v:i]
			#input0.sort()
			hashinput = str(input0)
			#insert into hashtable
			if hashinput in self.statemap.keys():
				hashval = self.statemap[hashinput]
				hashval[state] += 1
				self.statemap[hashinput] = hashval
			else:
				hashval = [0, 0, 0, 0, 0, 0, 0]
				hashval[state] += 1
				self.statemap[str(input0)] = hashval
				
		#after entering all counts, convert counts to percentages
		for k in self.statemap.keys():
			hashval = self.statemap[k]
			sumh = sum(hashval)
			hashval = [float(h) / sumh for h in hashval]
			self.statemap[k] = hashval
		
	
	#this function should calculate the "alternate state" for just a single data point.
	# recall that these states are computed based on what percentile of the data the value
	# lies in.
	def altsinglestatecalc(self, trdiff):
		t=trdiff
		if t < self.stdivs[0]:
			diffstate = 0
		elif t < self.stdivs[1]:
			diffstate = 1
		elif t < self.stdivs[2]:
			diffstate = 2
		elif t < self.stdivs[3]:
			diffstate = 3
		elif t < self.stdivs[4]:
			diffstate = 4
		elif t < self.stdivs[5]:
			diffstate = 5
		else:
			diffstate = 6
		return diffstate
		
	#this function should calculate "alternate states" for the entire training set based on
	#  what percentile of the data it lands within.
	def altstatecalc(self, trdata):
		trdiffs = [trdata[st] - trdata[st-1] for st in range(1, len(trdata))]
		strdiffs = sorted(trdiffs)
		stsize = len(trdata)/7
		#print "divs:"
		self.stdivs = [strdiffs[stsize], strdiffs[2*stsize], strdiffs[3*stsize], strdiffs[4*stsize], strdiffs[5*stsize], strdiffs[6*stsize]]
		diffstates=[]
		for t in trdiffs:
			diffstates += [self.altsinglestatecalc(t)]
		return diffstates
		
	#This function should compute an "expected change" value for each state computed
	# by the above functions.
	def computeexpectedchange(self, trdata):
		#compute the expected change for each state.
		#recall that 7 is the total number of states (should create a variable...)
		trdiffs = [trdata[st] - trdata[st-1] for st in range(1, len(trdata))]
		dataset = []
		for i in range(7):			
			if i == 0:
				dataset = [t for t in trdiffs if t < self.stdivs[0]]
			elif i == 6:
				dataset = [t for t in trdiffs if t > self.stdivs[5]]
			else:
				dataset = [t for t in trdiffs if (t < self.stdivs[i] and t > self.stdivs[i-1])]
			self.avgstatechange += [numpy.mean(dataset)]
		#print "here is the average state change: ",
		#print self.avgstatechange
				
		
		
	#IDEA FOR CHANGING THE BELOW FUNCTION: LET'S USE THE BINOMIAL DISTRIBUTION CDF TO COMPUTE
	#  THE PROBABILITY THAT INVESTING IN THIS STOCK REPEATEDLY WILL RESULT IN AT LEAST A SMALL GAIN.	
	#how to do this: calculate the expected amount lost from a loss; compute the expected amount
	#  gained from a gain, and multiply by the respective gain/loss probability to get the
	#  expected / adjusted gain/loss. Use this, plus the probability of the given outcome
	#  (from which we can guess the total number of occurrences in the future) to find the 
	#  probability of a slight gain (at least); this should be found using the Binomial CDF.
	#  If the result of the CDF is higher than a certain threshold, make an investment.

    #In this function, calculate the optimum amount of money to invest in order to maximize utility.
    # Inputs: number of state, probability vector, standard deviation, and old share price.
	def calcutil(self, stateprobs, sd, oldshareprice):
		nstates = 7 #this is the value we're going with for now, maybe change later...
		
		#util fn: "calcutil0" provided by the user.
		investmentvals = [float(self.m) * i / 8 for i in range(9)] #potential investment "tiers"
		utilities = []
		for investment in investmentvals:
			#for each possible investment size, compute the "utility" of making that investment
			#  based on the possibilities of risk.
			utility = 0
			for i in range(nstates):
				#calculate the newshareprice by adding the expected change from the "stdivs" variable
				newshareprice = oldshareprice + self.avgstatechange[i]
				moneychgratio = ((self.m - investment) + investment*newshareprice/oldshareprice)/self.m
				
				### NOTE: THIS IS WHAT SHOULD BE PASSED BY THE USER: A FUNCTION THAT RETURNS UTIL GIVEN MONEYCHGRATIO ###
				util0 = calcutil0(moneychgratio)
					
				utility += util0*stateprobs[i]
			utilities += [utility]
		
		## [DEBUG] print out the utilities:
		"""
		print "\nutils:",
		print [int(u*100) for u in utilities]
		"""
		
		#find optimum amount to invest and return that.
		optind = utilities.index(max(utilities))
		opt_investment = investmentvals[optind]
		return opt_investment



    #this function should take in one input data point and return a decision on how much money to invest.
    #the "predict_testdataset" function will then buy or sell the necessary shares and update your money.
	def predict_testinput(self, altzsinput, testdataval):
		#altzsinput.sort()
		hashinput = str(altzsinput)
		if hashinput in self.statemap.keys():
			stateprob = self.statemap[hashinput]
		else:
			#if there is no entry in the hashtable close to the current state, then assume
			#  that everything has an equal chance of happening.
			stateprob = [float(1)/7]*7
        #eventually, I should be solving an equation to find the optimum amount to invest to increase my
        #  utility should be a function of how much *money* you stand to lose or gain. It should vary depending
        #  on how much you invest, therefore.

        #The util function should return the amount of money I should invest.
		return self.calcutil(stateprob, self.sd, testdataval)

	#this function takes a test data set as input and repeatedly calls functions to
	#   find the optimum amount to invest. Then it invests that amount of money
	#   and tracks the size of the investment over time.
	#It also prints results to standard out and to an output text file.
	def predict_testdataset(self, testdataset, outfilepath='out.txt'):
		f=open(outfilepath, 'w')
		altzstestdata = [self.altsinglestatecalc(testdataset[st] - testdataset[st-1]) for st in range(1, len(testdataset))]
		#check how many of each value show up.
		#print "testdata:",
		#print "0: %d, 1: %d, 2: %d, 3: %d, 4: %d, 5: %d, 6: %d" % (altzstestdata.count(0), altzstestdata.count(1), altzstestdata.count(2),
		#	altzstestdata.count(3), altzstestdata.count(4), altzstestdata.count(5), altzstestdata.count(6))
		
		for i in range(self.v, len(testdataset)-2):
			#put the last "v" change states into the model and let it make a decision.
			altzsinput = altzstestdata[i-self.v: i]
			investment = self.predict_testinput(altzsinput, testdataset[i])
			
			
			#note: "testdataset[i+2]" should be the next closing price after investment decision is made. This is
			# because the z-scores should be one index behind the closing prices. Each zscore should be used to refer to the
			# closing price after the market change that the z-score measures.
			self.m = (self.m - investment) + investment*(testdataset[i+2]/testdataset[i+1])
			
			#record some results to standard out
			"""
			print "(inv: %f)" %investment,
			print self.m,
			print testdataset[i+1]
			"""
			
			#record some results to an output text file (for graphing)
			f.write("(inv: %f) %f %f" %(investment, self.m, testdataset[i+1]))
			if i < (len(testdataset)-3):
				f.write('\n')
			
		return self.m




