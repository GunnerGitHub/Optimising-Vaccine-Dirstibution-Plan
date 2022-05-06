"""Authors:
    Gunit Singh (47425704)
    Ben McGregor (46424800)
    Harrison Short (46475361)
MATH3202 Assignment 1: Linear Programming"""

from gurobipy import *

m = Model("Vaccination Distribution")

""" Data Provided """
IDtoLVC = [
[59.1,15.3,91.7,73.0,61.8,61.8,5.3,16.8],
[90.2,45.4,60.4,39.8,6.0,65.4,63.2,66.8],
[38.6,58.2,39.7,37.2,62.7,5.5,72.4,56.0]
]

CCDPop = [3210,3824,3535,2059,4436,2650,4260,3128,2652,2525,3533,2399,2298,2527,4797,3011,3495,3312,2889,2156,3801,2504,2151,2015,3779]

CCDtoLVC = [
[0,27.1,0,0,0,0,7.5,25.0],
[0,20.1,0,0,0,0,19.1,0],
[0,18.6,0,0,0,0,32.1,0],
[0,41.5,0,0,11.3,0,0,0],
[0,0,0,47.6,16.1,0,0,0],
[0,20.2,0,0,0,0,10.5,10.3],
[0,10.8,0,0,0,0,11.6,14.3],
[0,14.3,0,0,32.5,0,0,0],
[0,34.5,0,0,12.2,0,0,0],
[0,0,0,26.8,9.2,0,0,0],
[31.5,0,0,0,0,0,0,15.9],
[0,23.2,0,0,0,0,29.8,12.4],
[0,0,0,29.3,0,21.5,0,0],
[0,0,0,18.1,30.9,30.5,0,0],
[0,0,0,15.5,21.6,0,0,0],
[11.7,0,0,0,0,0,0,31.2],
[17.8,0,0,0,0,23.2,0,0],
[0,0,0,28.4,0,10.3,0,0],
[0,0,18.7,16.0,0,26.2,0,0],
[0,0,8.4,14.6,0,0,0,0],
[15.8,0,0,0,0,42.8,0,0],
[26.1,0,0,0,0,19.9,0,0],
[0,0,39.3,0,0,19.3,0,0],
[0,0,25.9,31.1,0,21.0,0,0],
[0,0,6.3,23.9,0,0,0,0]
]

""" Data Provided """

""" SETS """
Depots = ["ID-A (0)", "ID-B (1)", "ID-C(2)"]
V = range(len(Depots))

LocalCentre = ["LVC0","LVC1","LVC2","LVC3",
               "LVC4","LVC5","LVC6","LVC7"]
L = range(len(LocalCentre))

#A[i,j] gives the distance (km) from Id i to LVC j
A = {}
for n in range(len(Depots)):
    for c in range(len(IDtoLVC[n])):
        A[(n,c)] = IDtoLVC[n][c]
        

#B[i,j] gives the distance (km) from CDD i to LVC j
B= {}
for n in range(len(CCDtoLVC)):
    for c in range(len(CCDtoLVC[n])):
        B[(n,c)] = CCDtoLVC[n][c]

C = range(len(CCDPop))

Time = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"]

T = range(len(Time))

""" SETS """

""" DATA """

c1 = [144,105,157]

p = CCDPop

l1 = CCDtoLVC

l2 = IDtoLVC

d = 0.2

e = 1

Id = 31000

lv = 13000

lw = 1800

r=10

cf=0.1

""" DATA """

""" VARIABLES """
X = {}
for t in T:
    for a in A:
        X[t,a] = m.addVar()

Y = {}
for t in T:
    for b in B:
        Y[t,b] = m.addVar()
        
Z={}
for t in T:
    Z[t] = m.addVar()

""" VARIABLES """

""" OBJECTIVE FUNCTION """
m.setObjective(quicksum(c1[v]*X[t,a] for t in T for v in V for a in A if a[0]==v) 
               +quicksum(A[a]*d*X[t,a] for t in T for a in A)
               +quicksum(B[b]*e*Y[t,b] for t in T for b in B)
               +quicksum(r*Z[t] for t in T),
               GRB.MINIMIZE)
""" OBJECTIVE FUNCTION """

""" CONSTRAINTS """

#the total amount of vaccines going to a CCD from its neighbouring LVC’s must be equivalent to the population of the CCD.
for c in C:
    m.addConstr(quicksum(Y[t,b] for t in T for b in B if b[0]==c)==p[c])

#the demand of vaccines at an LVC, as the vaccines flowing out of it in a week must be equivalent to those flowing into it.
for t in T:
    for l in L:
        m.addConstr(quicksum(X[t,a] for a in A if a[1]==l) 
                    == quicksum(Y[t,b] for b in B if b[1]==l)) #note B has opposite ke 
        
#the citizens of CCD’s are only able to obtain the vaccine from a neighbouring LVC (as a distance of 0km in the data represents a non-neighbouring LVC).
for t in T:
    for b in B:
        if B[b]==0:
            m.addConstr(Y[t,b]==0)

#Vaccines imported at ID's must be less than its capacity throguh the whole operation
for v in V:
    m.addConstr(quicksum(X[t,a] for t in T for a in A if a[0]==v)<=Id)

#Vaccines administered at LVC must be less than its capacity throguh the whole operation
for l in L:
    m.addConstr(quicksum(X[t,a] for t in T for a in A if a[1] == l)<=lv)

#the maximum number of weekly doses that can be delivered at an LVC at any given week is not exceeded
for t in T:
    for l in L:
        m.addConstr(quicksum(X[t,a] for a in A if a[1]==l)<=lw)

#the number of unvaccinated people each week, which is used in the objective function to account for delayed vaccinations.
for t in T:
    m.addConstr(Z[t]==(quicksum(p[c] for c in C)-quicksum(Y[t1,b]  for t1 in T if t1<=t for b in B)))


#the differences between the fraction of the population vaccinated in each CCD at a given week does not vary significantly
for t in T:
    for c in C:
        for cc in C:
            m.addConstr((((quicksum(Y[t1,b] for t1 in T if t1<=t for b in B if b[0] == c))/p[c])
                        -((quicksum(Y[t1,b] for t1 in T if t1<=t for b in B if b[0] == cc))/p[cc]))
                        <=cf)

""" CONSTRAINTS """

""" OPTIMISE and FINAL ANSWER """
m.optimize()

print("Total vaccines produced in the operation was",sum(X[t,a].x for t in T for a in A))
    
print("Total cost of the operation is", m.objval)

""" OPTIMISE and FINAL ANSWER """
