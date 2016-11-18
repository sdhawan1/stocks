
## Create an hmm model for the purpose of making investment decisions.

import numpy

class stockhmm(object):
    m = 0
    s = 0
    v = 0
    sd = 0
    statemap = {}
    #FIGURE OUT HOW TO ADD FUNCTION "UTILFN"

    def statecalc(close0, close1):
        #round all zscores down to the smaller-magnitude integer part.
        zscore = abs(close1-close0)/self.sd
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


    #initially, we should set "trdata" equal to a full list of closing prices only.
    #"utilfn" = the utility function we want for our data.
    def __init__(self, smoothness, visibility, trdata, utilfn, money):
        #input basic tests after I learn exception handling

        #take the training data and fill out our HMM. Every training input (sorted)
        # should map to a set of probabilities, each corresponding to how likely
        # the next state is.
        self.m = money
        self.s = smoothness
        self.v = visibility

        #"smooth" the trdata so that there are 1/s the number of original inputs;
        #  let every s closing values be averaged to create a new one in a modified list.
        moddata = []
        for i in range(0, len(trdata), self.s):
            moddata += [numpy.mean(trdata[i-self.s, i])]
        trdata = moddata

        #calculate sd of closing price differences: important later on:
        self.sd = numpy.std( [trdata[a] - trdata[a-1] for a in range(1, len(trdata))] )

        #the statemap's input should be every possible combination of five states (sorted)
        #iterate through the training data and store data in the statemap
        for i in range(self.v, len(trdata)):
            input0 = trdata[i-self.v, i]
            input0.sort()
            hashinput = str(input0)
            state = self.statecalc(input0[-1], input0[-2])

            #insert into hashtable
            if hashinput in statemap.keys():
                hashval = statemap[hashinput]
                hashval[state] += 1
                statemap[hashinput] = hashval
            else:
                hashval = [0, 0, 0, 0, 0, 0, 0]
                hashval[state] += 1
                statemap[str(input0)] = hashval
                
        #after entering all counts, convert counts to percentages
        for k in statemap.keys():
            hashval = statemap[k]
            sumh = sum(hashval)
            hashval = [float(h) / sumh for h in hashval]


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
    def predict_testinput(testinput):
        hashinput = str(testinput.sort())
        stateprob = self.statemap[hashinput]
        #eventually, I should be solving an equation to find the optimum amount to invest to increase my utility
        #  utility should be a function of how much *money* you stand to lose or gain. It should vary depending
        #  on how much you invest, therefore.

        #The util function should return the amount of money I should invest.
        return self.calcutil(stateprob, self.sd, testinput[-1])

    def predict_testdataset(testdataset):
        for i in range(self.v, len(testdataset)):
            input0 = testdataset[i-self.v, i]
            investment = predict_testinput(input0)
            #amount of money you don't invest is unchanged. The rest of the money grows in accordance with the
            # ratio of the growth of the stock price
            #  [ACTION REQUIRED: THINK ABOUT THIS EQUATION SOME MORE...]
            self.m = (self.m - investment) + investment*(testdataset[i]/testdataset[i-1])
