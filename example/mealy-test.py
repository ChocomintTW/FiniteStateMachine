import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from fsm.machine import *
from fsm.assign import *
from fsm.optimize import calcBest

s0, s1, s2, s3, s4, s5 = createStatesByCount(6)

m = MealyMachine(symbols("X"), symbols("Z"))
m.addState(s0, (s4, s1), (0, 0))
m.addState(s1, (s2, s1), (0, 0))
m.addState(s2, (s3, s1), (1, 0))
m.addState(s3, (s3, s5), (0, 0))
m.addState(s4, (s3, s1), (0, 0))
m.addState(s5, (s2, s1), (1, 0))

print(m.transitionTable())
print()

m.graph().render(directory="example", filename="mealy1", format="png", cleanup=True)

best_cost, best = calcBest(m)

# print(len(best), "distinct assignments")
print("Assignment:")
assignment = best[0]
print(assignment)
print()

eqs = deriveEquations(m, assignment)
eqs.printAll()

print(f"\n{best_cost} gate inputs")