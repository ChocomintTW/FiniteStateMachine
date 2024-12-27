from fsm.machine import *
from fsm.utils import simply
from sympy.logic import gateinputcount
from typing import Any

class AssignError(Exception): ...

class Assignment:
	def __init__(self, mapping: dict[State, str]):
		self.mapping = mapping

	def get(self, state: State):
		return self.mapping[state]

	def states(self):
		return self.mapping.keys()

	def values(self):
		return self.mapping.values()
	
	def __str__(self):
		return "\n".join([f"{str(state)}: {s}" for state, s in sorted(self.mapping.items(), key=lambda tp: str(tp[0]))])

def isEquiv(assign1: Assignment, assign2: Assignment):
	if set(assign1.states()) != set(assign2.states()):
		return False
	
	assignList1 = list(map(lambda tp: tp[1], sorted(assign1.mapping.items(), key=lambda tp: str(tp[0]))))
	assignList2 = list(map(lambda tp: tp[1], sorted(assign2.mapping.items(), key=lambda tp: str(tp[0]))))
	n = len(assignList1[0])

	columns1 = set(["".join([s[i] for s in assignList1]) for i in range(n)])
	columns2 = set(["".join([s[i] for s in assignList2]) for i in range(n)])
	
	return columns1 == columns2

class Equations:
	def __init__(self, nxtEqs: dict, outEqs: dict, inputs: tuple[Symbol], outputs: tuple[Symbol]):
		self.nxtEqs = nxtEqs
		self.outEqs = outEqs
		self.inputs = inputs
		self.outputs = outputs
	
	def totalGateInputCount(self):
		return self.totalCost(gateinputcount)
	
	def totalCost(self, costFunction: Callable[[Any], int]):
		return sum(map(costFunction, self.nxtEqs.values())) + sum(map(costFunction, self.outEqs.values()))

	def __prt(self, d: dict):
		for x, eq in d.items():
			print(f"{x} = {simply(eq)}")
	
	def printAll(self):
		print("Next State Equations:")
		self.__prt(self.nxtEqs)
		print("\nOutput Equations:")
		self.__prt(self.outEqs)

def deriveEquations(machine: Machine, assignment: Assignment):
	ffs = len(list(assignment.values())[0])
	if not all(len(s) == ffs for s in assignment.values()):
		raise AssignError("Invalid assignment length.")
	
	if len(set(assignment.values())) != len(assignment.values()):
		raise AssignError("Assignments should not be identical.")

	# TODO: make it customable by user
	ff = symbols([chr(i) for i in range(ord('A'), ord('A') + ffs)])

	# next states
	nextMinterms = [[] for _ in range(ffs)]
	COMBINATIONS = machine.inputCombinations()
	for state in machine.states():
		for input in COMBINATIONS:
			location = assignment.get(state) # find this location (combine with input)
			value = assignment.get(machine.nextStateTable.next(state, input)) # input this value into it
			for idx in range(ffs):
				if value[idx] == '1':
					nextMinterms[idx].append(int(input + location, base=2))

	# don't-cares
	d2b_func = lambda s: int(s, base=2)
	dc = set([f"{i:0{ffs}b}" for i in range(0, 2**ffs)]) - set(assignment.values())
	dontcares = list(map(d2b_func, flatten([[input + d for d in dc] for input in COMBINATIONS])))
	
	# outputs
	outputEqs: dict
	if type(machine) == MealyMachine:
		osize = machine._outputSize
		outputMinterms = [[] for _ in range(osize)]
		for state in machine.states():
			for input in COMBINATIONS:
				location = assignment.get(state)
				value = machine._mergedTable().loc[state][input]
				for idx in range(osize):
					if value[idx] == '1':
						outputMinterms[idx].append(int(input + location, base=2))
		outputEqs = { machine._outputs[idx]: SOPform(list(machine._inputs) + list(ff), outputMinterms[idx], dontcares) for idx in range(osize) }
	
	elif type(machine) == MooreMachine:
		osize = machine._outputSize
		outputMinterms = [[] for _ in range(osize)]
		for state in machine.states():
			for input in COMBINATIONS:
				location = assignment.get(state)
				value = machine._mergedTable().loc[state]
				for idx in range(osize):
					if value[idx] == '1':
						outputMinterms[idx].append(int(location, base=2))
		outputEqs = { machine._outputs[idx]: SOPform(list(ff), outputMinterms[idx], list(map(d2b_func, dc))) for idx in range(osize) }
	
	next_ff = [symbols(f"{str(sym)}+") for sym in ff]
	nextStateEqs = { next_ff[idx]: SOPform(list(machine._inputs) + list(ff), nextMinterms[idx], dontcares) for idx in range(ffs) }

	return Equations(nextStateEqs, outputEqs, machine._inputs, machine._outputs)

def deriveEquations_OneHot(machine: Machine):
	mapping = {}
	n = len(machine.states())
	for idx, state in enumerate(machine.states()):
		mapping[state] = f"{2**(n-idx-1):0{n}b}"
	return deriveEquations(machine, Assignment(mapping))