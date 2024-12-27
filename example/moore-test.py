import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from fsm.machine import *
from fsm.assign import *
from fsm.optimize import calcBest

s0, s1, s2, s3, s4 = createStatesByCount(5)

m = MooreMachine(symbols("X"), symbols("Z"))
m.addState(s0, (s0, s1), 1)
m.addState(s1, (s2, s4), 0)
m.addState(s2, (s0, s3), 1)
m.addState(s3, (s2, s0), 0)
m.addState(s4, (s1, s3), 1)

print(m.transitionTable())
print()

best_cost, best = calcBest(m)

# print(len(best), "distinct assignments")
print("Assignment:")
assignment = best[0]
print(assignment)
print()

eqs = deriveEquations(m, assignment)
eqs.printAll()

print(f"\n{best_cost} gate inputs")