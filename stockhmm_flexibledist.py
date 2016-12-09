
## Create an hmm model for the purpose of making investment decisions.

#Current findings: the algorithm has very high performance. It makes dramatic
#   gains in stock price, even over periods where the stock it's tracking went down.
#Next steps: (1) commit this code to the github repository
#   (2) document the math that went into making this algorithm (create graphs).
#   (3) perform more testing - k fold cross validation + other stocks.

import numpy
import csv
import math

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
		
		print "\naltzstrdata:"
		print "0: %d, 1: %d, 2: %d, 3: %d, 4: %d, 5: %d, 6: %d\n" % (altzstrdata.count(0), altzstrdata.count(1), altzstrdata.count(2),
			altzstrdata.count(3), altzstrdata.count(4), altzstrdata.count(5), altzstrdata.count(6))
		
		
		#the statemap's input should be every possible combination of five states (sorted)
		#iterate through the training data and store data in the statemap
		for i in range(self.v, len(altzstrdata)):
			state = altzstrdata[i] 
			#we want to scale up [-3, 3] -> [0, 6]			input0 = zscoretrdata[(i-self.v):i]
			input0 = altzstrdata[i-self.v:i]
			input0.sort()
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

			
			
    #calculate the "adjusted" z-score for the given value
	#Idea: instead of making it only 0, 1, 2, 3, make it 0.2, 0.6, 1.6 (equitable AUC).
	def statecalc(self, close0, close1):
		modzscore = 0
		mzscoresign = 1
		#note: the below assumes that the mean of the differences is 0 (may or may not be accurate!!!)
		zscore = abs(close1-close0)/(self.sd)
		if close1 < close0:
			mzscoresign = -1
		#lump zscores with value > 3 into one state
		if zscore > 1.16:
			modzscore = 3
		elif zscore > 0.6:
			modzscore = 2
		elif zscore > 0.2:
			modzscore = 1
		else:
			modzscore = 0
		modzscore *= mzscoresign
		#finally, shift all states so the lowest state is zero
		state = modzscore + 3
		return state
		
	
	#this function should calculate the "alternate state" for just a single data point.
	# recall that these states are computed based on what percentile of the data the value
	# lands in.
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
		print "divs:"
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
		print "here is the average state change: ",
		print self.avgstatechange
				
		
		
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
		
		#util fn: logarithmic for (ratio) money loss, linear for money gain? [good for now]
		#if we're very risk-averse, we can also do logarithmic for money gain
		investmentvals = [float(self.m) * i / 8 for i in range(8)] #potential investment "tiers"
		utilities = []
		for investment in investmentvals:
			#for each possible investment size, compute the "utility" of making that investment
			#  based on the possibilities of risk.
			
			#[DEBUG]: figure out why the utilities are so skewed towards no investment.
			"""
			print "\ninvestment: %d\n" % investment
			"""
			
			utility = 0
			for i in range(nstates):
				#calculate the newshareprice by adding the expected change from the "stdivs" variable
				newshareprice = oldshareprice + self.avgstatechange[i]
				moneychgratio = ((self.m - investment) + investment*newshareprice/oldshareprice)/self.m
				
				### NOTE: THIS IS WHAT SHOULD BE PASSED BY THE USER: A FUNCTION THAT RETURNS UTIL GIVEN MONEYCHGRATIO ###
				if moneychgratio < 1:
					util0 = numpy.log(moneychgratio)+1
				else:
					util0 = moneychgratio
				
				#[DEBUG]: figure out why the utilities are so skewed towards no investment.
				"""
				print "mch: %f, util: %f ---" %(moneychgratio, util0),
				"""
				#DEBUG: WHY ARE THERE NAN UTIL0'S?
				"""				
				if math.isnan(util0):
					print "NAN UTIL0:",
					print moneychgratio,
					print investment,
					print newshareprice,
					print oldshareprice
					"""
				
				
				utility += util0*stateprobs[i]
				
			#[DEBUG]: figure out why the utilities are so skewed towards no investment.
			"""
			print "total: %f" % utility,
			"""
			
			utilities += [utility]
		
		## [DEBUG] print out the utilities:
		"""
		print "\nutils:",
		print [int(u*100) for u in utilities]
		"""
		
		#find optimum amount to invest and return that.
		optind = utilities.index(max(utilities))
		opt_investment = investmentvals[optind]
		#Print investment amount:
		print "(inv: %f)" %opt_investment
		return opt_investment



    #this function should take in one input data point and return a decision on how much money to invest.
    #the "predict_testdataset" function will then buy or sell the necessary shares and update your money.
	def predict_testinput(self, altzsinput, testdataval):
		altzsinput.sort()
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
		
		#[DEBUG] understand why the util function never invests.
		"""		
		print hashinput,
		print [int(s*100) for s in stateprob],
		"""
		
		return self.calcutil(stateprob, self.sd, testdataval)

	def predict_testdataset(self, testdataset):
		altzstestdata = [self.altsinglestatecalc(testdataset[st] - testdataset[st-1]) for st in range(1, len(testdataset))]
		#check how many of each value show up.
		print "testdata:",
		print "0: %d, 1: %d, 2: %d, 3: %d, 4: %d, 5: %d, 6: %d" % (altzstestdata.count(0), altzstestdata.count(1), altzstestdata.count(2),
			altzstestdata.count(3), altzstestdata.count(4), altzstestdata.count(5), altzstestdata.count(6))
		
		for i in range(self.v, len(testdataset)-2):
			#put the last "v" change states into the model and let it make a decision.
			altzsinput = altzstestdata[i-self.v: i]
			investment = self.predict_testinput(altzsinput, testdataset[i])
			#[DEBUG] figure out why no investment:
			"""
			#print investment,
			"""
			
			#  [ACTION REQUIRED: THINK ABOUT THIS EQUATION SOME MORE...]
			#note: "testdataset[i+2]" should be the next closing price after investment decision is made. This is
			# because the z-scores should be one index behind the closing prices. Each zscore should be used to refer to the
			# closing price after the market change that the z-score measures.
			self.m = (self.m - investment) + investment*(testdataset[i+2]/testdataset[i+1])
			print self.m,
		return self.m

		
#here, try to test the above data structure.

#start out by retrieving data for one stock and training it.
f = open("data/aapl_10yrs.csv")
aapl = list(csv.reader(f))
colnames = aapl[0]
aapl = aapl[2:]
trdata = [float(a[1]) for a in aapl[:2000]]
testdata = [float(a[1]) for a in aapl[2000:]]

#now, train our model. Smoothness and visibility are 3, and money is 1000
h = stockhmm(2, 2, trdata, 1000)


#test our model by calling "predict" with the trained hmm on the test data.
#DEBUGGING: MAKE THE TEST DATA MORE MANAGEABLE:
#testdata = testdata[:365]
money = h.predict_testdataset(testdata)
print ""
print "end balance: %f" % money
print "start: %f" % testdata[0],
print "end: %f" % testdata[-1]





