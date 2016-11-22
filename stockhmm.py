
## Create an hmm model for the purpose of making investment decisions.

import numpy

class stockhmm(object):
    m = 0
    s = 0
    v = 0
    sd = 0
    statemap = {}
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

        #"smooth" the trdata so that there are 1/s the number of original inputs;
        #  let every s closing values be averaged to create a new one in a modified list.
        moddata = []
        for i in range(self.s, len(trdata), self.s):
            nextval = numpy.mean(trdata[i-self.s: i])
            moddata += [nextval]
        trdata = moddata

        #calculate sd of closing price differences: important later on:
        self.sd = numpy.std( [trdata[a] - trdata[a-1] for a in range(1, len(trdata))] )

        #translate the closing prices into z-scores.
        zscoretrdata = [self.statecalc(st-1, st) for st in range(1, len(trdata))]

        #the statemap's input should be every possible combination of five states (sorted)
        #iterate through the training data and store data in the statemap
        for i in range(self.v, len(zscoretrdata)):
            input0 = zscoretrdata[i-self.v: i]
            input0.sort()

            #[!!!ERROR!!!] WE NEED THE HASH INPUT TO HAVE VALUES DICTATED BY THE *Z-SCORES* OF TRDATA!!!!
            #resolved?

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

    #calculate the "adjusted" z-score for the given value
    def statecalc(self, close0, close1):
        zscore = abs(close1-close0)/(self.sd + .0001)
        zscore = int(zscore)
        if close1 < close0:
            zscore = -1*zscore
        #lump zscores with value > 3 into one state
        if zscore > 3:
            zscore = 3
        elif zscore < -3:
            zscore = -3
        #finally, shift all states so the lowest state is zero
        state = zscore + 3
        return state


    #In this function, calculate the optimum amount of money to invest in order to maximize utility.
    # Inputs: number of state, probability vector, standard deviation, and old share price.
    def calcutil(stateprobs, sd, oldshareprice):
        nstates = 7 #this is the value we're going with for now, maybe change later...
	statetozval = [s-3 for s in range(nstates)]
	
	#util fn: logarithmic for (ratio) money loss, linear for money gain? [good for now]
	#if we're very risk-averse, we can also do logarithmic for money gain
	investmentvals = [float(money) * i / 8 for i in range(8)]
	utilities = []
	for investment in investmentvals:
		#for each possible investment size, compute the "utility" of making that investment
		#  based on the possibilities of risk.
		utility = 0
		for i in range(nstates):
			newshareprice = oldshareprice + sd*statetozval[i]
			moneychgratio = ((self.m - investment) + investment*newshareprice/oldshareprice)/self.m
			### NOTE: THIS IS WHAT SHOULD BE PASSED BY THE USER: A FUNCTION THAT RETURNS UTIL GIVEN MONEYCHGRATIO ###
			if moneychgratio < 1:
				util0 = numpy.log(moneychgratio)
			else:
				util0 = moneychgratio				
			utility += util0*stateprobs[i]
		
		utilities += [utility]
		
	#find optimum amount to invest and return that.
	optind = utilities.index(max(utilities))
	opt_investment = investmentvals[optind]
	return opt_investment



    #this function should take in one input data point and return a decision on how much money to invest.
    #the "predict_testdataset" function will then buy or sell the necessary shares and update your money.
    def predict_testinput(self, zscoreinput):
        zscoreinput.sort()
        hashinput = str(zscoreinput)
        stateprob = self.statemap[hashinput]
        #eventually, I should be solving an equation to find the optimum amount to invest to increase my
        #  utility should be a function of how much *money* you stand to lose or gain. It should vary depending
        #  on how much you invest, therefore.

        #The util function should return the amount of money I should invest.
        return self.calcutil(stateprob, self.sd, testinput[-1])

    def predict_testdataset(self, testdataset):
        zscoretestdata = [self.statecalc(st-1, st) for st in range(1, len(testdataset))]
        for i in range(self.v, len(testdataset)):
            zscoreinput = zscoretestdata[i-self.v: i]
            print zscoreinput
            #investment = self.predict_testinput(input0)
            #DEBUG: MAKING SURE EVERYTHING IS WORKING PROPERLY...
            investment = self.predict_testinput(range(1, self.v))

            #amount of money you don't invest is unchanged. The rest of the money grows in accordance with the
            # ratio of the growth of the stock price
            #  [ACTION REQUIRED: THINK ABOUT THIS EQUATION SOME MORE...]
            #note: "testdataset[i+2]" should be the next closing price after investment decision is made. This is
            # because the z-scores should be one index behind the closing prices. Each zscore should be used to refer to the
            # closing price after the market change that the z-score measures.
            self.m = (self.m - investment) + investment*(testdataset[i+2]/testdataset[i+1])
        return self.m
