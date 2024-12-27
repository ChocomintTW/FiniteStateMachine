from sympy import *
import pandas as pd
import re

class State:
	def __init__(self, name: str):
		self.name = name
	
	def __str__(self):
		return self.name

def createStates(names: str):
	"""
		Generate states by `symbols` function from sympy
	"""
	return tuple(map(State, map(str, symbols(names))))

def createStatesByCount(n: int):
	"""
		Generate states from `S0` to `S(n-1)`
	"""
	return createStates(f"S:{n}")

class StateError(Exception): ...

class NextStateTable:
	def __init__(self, inputs: tuple[Symbol] | Symbol):
		if type(inputs) == Symbol:
			n = 1
		else:
			n = len(inputs)
		self.n = n
		self.__count = 2**n
		self.table = pd.DataFrame(columns=[f"{i:0{n}b}" for i in range(0, 2**n)])
	
	def addState(self, state: State, nexts: tuple[State]):
		if len(nexts) != self.__count:
			raise StateError(f"Invalid next states count (Expected: {self.__count})")
		if state in self.table.index:
			raise StateError(f"Duplicated state: {state}")
		self.table.loc[state] = nexts

	def next(self, state: State, input: str):
		if len(input) != self.n or not re.match(r"^[01]*$", input):
			raise Exception("Invalid input")
		return self.table.loc[state][input]
