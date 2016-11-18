
#create a function that takes in the probabilities of all inputs of the HMM
#  and generates the monetary investment value that returns the optimal utility

import numpy

utilfn(money, nstates, stateprobs, sd, oldshareprice):
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
			moneychgratio = ((money - investment) + investment*newshareprice/oldshareprice)/money
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
	
	
	
	### create new properties files: the qa property file should have url: jdbc:sybase:Tds:vhascqq1db:2641/DQ1_NLS?charset=iso_1
