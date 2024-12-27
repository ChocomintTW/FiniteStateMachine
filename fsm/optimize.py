from fsm.machine import *
from fsm.assign import *
from itertools import permutations
import math

def fingerprint(assignment: Assignment):
	lst = list(map(lambda tp: tp[1], sorted(assignment.mapping.items(), key=lambda tp: str(tp[0]))))
	return frozenset(["".join([s[i] for s in lst]) for i in range(len(lst[0]))])

def calcBest(machine: Machine, costFunction: Callable[[Any], int] = gateinputcount):
	"""
	Set first-added state as the reset state.\n
	Equivalent assignments are eliminated
	"""
	n = len(machine.states())
	ffs = math.ceil(math.log2(n))

	permutationSet = set(permutations(machine.states()[1:]+[None]*(2**ffs-n)))

	# brute-forced
	seen = set()
	assignments: list[Assignment] = []
	for p in permutationSet:
		mapping = { machine.states()[0]: f"{0:0{ffs}b}" }
		for i, state in enumerate(p):
			if state != None:
				mapping[state] = f"{(i+1):0{ffs}b}"
		assign = Assignment(mapping)
		val = fingerprint(assign)
		if val not in seen:
			seen.add(val)
			assignments.append(assign)
	
	assignmentPairs: list[tuple[int, Assignment]] = []
	for assign in assignments:
		eqs = deriveEquations(machine, assign)
		assignmentPairs.append((eqs.totalCost(costFunction), assign))

	assignmentsByCost = sorted(assignmentPairs, key=lambda tp: tp[0])
	best_cost = assignmentsByCost[0][0]
	best = list(map(lambda e: e[1], filter(lambda tp: tp[0] == best_cost, assignmentsByCost)))

	return best_cost, best