
#create a function that takes in the moneychangeratio, which
# is the ratio: futuremoney/currentmoney. The output is the
# utility of the operation that will cause you to end up with
# the amount "futuremoney".
#For example, a logarithmic utility function will give zero
# utility if you don't gain money, and will give you exponenti-
# ally increasing negative utility if you lose money. As a re-
# sult, this is a very risk-averse utility function.

import numpy

#risk averse: logarithmic for loss, linear for gain.
"""
def calcutil0(moneychangeratio):
	mcr = moneychangeratio
	if mcr < 1:
		util0 = numpy.log(mcr)+1
	else:
		util0 = mcr
	return util0
		
"""


#cubic in gain and loss: averse to heavy risk, loves heavy gain.
"""
def calcutil0(moneychangeratio):
	mcr = moneychangeratio
	util0 = (mcr-1)**3
	return util0
"""

#risk loving: exponential for gain, linear for loss. This will
#  approximate the actual market much more closely.
"""
def calcutil0(moneychangeratio):
	mcr = moneychangeratio
	if mcr < 1:
		util0 = mcr
	else:
		util0 = 2**mcr-1
	return util0
"""


#exprisk: loves risk even more than the risk-loving model.
# surprisingly it is about the same as the risk-loving; even
# doing worse over the very long term. Perhaps avoiding some risk is
# very important.
"""
def calcutil0(moneychangeratio):
	mcr = moneychangeratio
	util0 = 2**mcr-1
	return util0
"""

#linear: the model that filters the HMM least
def calcutil0(moneychangeratio):
	mcr = moneychangeratio
	util0 = mcr
	return util0
