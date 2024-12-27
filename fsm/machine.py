from fsm.state import *
from typing import Callable
import graphviz as gv

class Machine:
	# variables
	nextStateTable: NextStateTable
	_inputs: tuple[Symbol]
	_outputs: tuple[Symbol]
	_inputSize: int
	_outputSize: int
	_count: int

	def __init__(self, inputs: tuple[Symbol] | Symbol, outputs: tuple[Symbol] | Symbol):
		self.nextStateTable = NextStateTable(inputs)

		self._inputs = (inputs,) if type(inputs) == Symbol else inputs
		self._outputs = (outputs,) if type(outputs) == Symbol else outputs

		self._inputSize = len(self._inputs)
		self._outputSize = len(self._outputs)
		self._count = 2**self._inputSize

	def addState(self, state: State, nexts: tuple[State]):
		self.nextStateTable.addState(state, nexts)

	def graph(
			self,
			outputTableModified: pd.DataFrame,
			arrowLabel: Callable[[pd.Index, list, int], str],
			isMoore: bool,
			k
		):
		g = gv.Digraph()
		g.attr(splines="true", layout="fdp", K=str(k))

		table = pd.concat([self.nextStateTable.table, outputTableModified], axis=1)
		for state in table.index:
			if isMoore:
				g.node(state.name, label=f"<<U>{state.name}</U><BR/><FONT COLOR=\"blue\">{outputTableModified.loc[state]}</FONT>>", shape="circle")
			else:
				g.node(state.name, label=state.name, shape="circle")

		edges = {}
		for state, row in table.iterrows():
			lst = list(row)
			for i in range(0, self._count):
				s = arrowLabel(table.columns, lst, i)
				if (state, lst[i]) in edges.keys():
					edges[(state, lst[i])] += ", " + s
				else:
					edges[(state, lst[i])] = s

		for (tail, head), label in edges.items():
			g.edge(tail.name, head.name, label, fontcolor="blue")

		return g

	def inputCombinations(self) -> list[str]:
		n = self._inputSize
		return [f"{i:0{n}b}" for i in range(0, 2**n)].copy()

	def states(self) -> list[State]:
		return list(self.nextStateTable.table.index)

class MealyMachine(Machine):
	# variables
	outputTables: dict[Symbol, pd.DataFrame]

	def __init__(self, inputs: tuple[Symbol] | Symbol, outputs: tuple[Symbol] | Symbol):
		super().__init__(inputs, outputs)

		if self._outputSize == 1:
			self.outputTables = { outputs: pd.DataFrame(columns=self.inputCombinations()) }
		else:
			self.outputTables = {}
			for i in range(self._outputSize):
				self.outputTables[outputs[i]] = pd.DataFrame(columns=self.inputCombinations())
	
	def addState(self, state: State, nexts: tuple[State], outputsList: list[tuple[bool]] | tuple):
		super().addState(state, nexts)

		if self._outputSize == 1:
			if len(outputsList) != self._count:
				raise Exception(f"Invalid outputs count (Expected: {self._count})")
			self.outputTables[self._outputs[0]].loc[state] = outputsList
		else:
			if len(outputsList) != self._outputSize:
				raise Exception(f"Invalid output list count (Expected: {self._outputSize})")
			for idx, ops in enumerate(outputsList):
				if len(ops) != self._count:
					raise Exception(f"Invalid outputs count (Expected: {self._count})")
				self.outputTables[self._outputs[idx]].loc[state] = ops

	def _mergedTable(self):
		lst = list(self.outputTables.values())
		mergedTable = lst[0].astype(str)
		for i in range(1, len(self._outputs)):
			mergedTable += lst[i].astype(str)
		return mergedTable
	
	def transitionTable(self, merge=False):
		if merge:
			t = pd.concat([self.nextStateTable.table, self._mergedTable()], axis=1)
			t.columns = pd.MultiIndex.from_product([
				["".join(map(str, self._inputs)), "".join(map(str, self._outputs))],
				self.inputCombinations()
			])
		else:
			t = pd.concat([self.nextStateTable.table]+list(self.outputTables.values()), axis=1)
			t.columns = pd.MultiIndex.from_product([
				["".join(map(str, self._inputs))]+list(map(str, self._outputs)),
				self.inputCombinations()
			])
		return t

	def graph(self, k=1.3):
		arrowLabel = lambda columns, lst, i: columns[i] + "/" + str(lst[self._count + i])
		return super().graph(self._mergedTable(), arrowLabel, False, k)

class MooreMachine(Machine):
	# variables
	outputTable: pd.DataFrame

	def __init__(self, inputs: tuple[Symbol] | Symbol, outputs: tuple[Symbol] | Symbol):
		super().__init__(inputs, outputs)
		if type(outputs) == Symbol:
			self.outputTable = pd.DataFrame(columns=[str(outputs)])
		else:
			self.outputTable = pd.DataFrame(columns=list(map(str, outputs)))
	
	def addState(self, state: State, nexts: tuple[State], outputsList: list[bool] | bool):
		super().addState(state, nexts)
		self.outputTable.loc[state] = outputsList

	def _mergedTable(self):
		return self.outputTable.apply(lambda row: "".join(row.astype(str)), axis=1)
	
	def transitionTable(self):
		t = pd.concat([self.nextStateTable.table, self._mergedTable()], axis=1)
		t.columns = self.inputCombinations() + ["".join(map(str, self._outputs))]
		return t

	def graph(self, k=1.3):
		return super().graph(
			self._mergedTable(),
			lambda columns, _, i: columns[i],
			True,
			k
		)
