from sympy.logic import *

def gateCount(expr):
	if isinstance(expr, (And, Or)):
		return 1 + sum(gateCount(arg) for arg in expr.args)
	return 0