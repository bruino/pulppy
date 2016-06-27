#!/usr/bin/env python
# @(#) $Jeannot: test1.py,v 1.11 2005/01/06 21:22:39 js Exp $

# Import PuLP modeler functions
from pulp import *

# A new LP problem
prob = LpProblem("Example", LpMinimize)

# Variables
# 0 <= x <= 4
x = LpVariable("x", 0, None)
# -1 <= y <= 1
y = LpVariable("y", 0, None)

# Use None for +/- Infinity, i.e. z <= 0 -> LpVariable("z", None, 0)

# Objective
prob += -40*x - 30*y, "obj"
# (the name at the end is facultative)

c1 = 0.4*x + 0.5*y <= 20
c2 = 0.2*y <= 5
c3 = 0.6*x + 0.3*y <= 21
# Constraints
prob += c1, "c1"
prob += c2, "c2"
prob += c3, "c3"
# (the names at the end are facultative)

# Write the problem as an LP file
prob.writeLP("test1.lp")

# Solve the problem using the default solver
# coinor-cbc
prob.solve(COIN())
# Use prob.solve(GLPK()) instead to choose GLPK as the solver
# Use GLPK(msg = 0) to suppress GLPK messages
# If GLPK is not in your path and you lack the pulpGLPK module,
# replace GLPK() with GLPK("/path/")
# Where /path/ is the path to glpsol (excluding glpsol itself).
# If you want to use CPLEX, use CPLEX() instead of GLPK().
# If you want to use XPRESS, use XPRESS() instead of GLPK().
# If you want to use COIN, use COIN() instead of GLPK(). In this last case,
# two paths may be provided (one to clp, one to cbc).

# Print the status of the solved LP
print("Status:", LpStatus[prob.status])

# Print the value of the variables at the optimum
for v in prob.variables():
	print(v.name, "=", v.varValue)

# Print the value of the objective
print("objective=", value(prob.objective))

#print dir(prob)
#print '-------------'
#print dir(pulp.LpConstraint)
print "Shadow Price"
print c1.pi
print c2.pi
print c3.pi
print "Slack or Surplus"
print c1.slack
print c2.slack
print c3.slack
print "Reduce Cost"
print x.dj
print y.dj
