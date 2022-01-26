from pyomo.environ import *
import pandas as pd

# Products
products = {
    'P1' : {'ACR' : 40, 'labor': 2,   'demand': 400},
    'P2' : {'ACR' : 30, 'labor': 1,   'demand': 400},
    'P3' : {'ACR' : 20, 'labor': 0.5, 'demand': 400},
    'P4' : {'ACR' : 25, 'labor': 0.5, 'demand': 400},
    'P5' : {'ACR' : 45, 'labor': 2,   'demand': 400}
}

factory = {'F1' : {'production' : 1000, 'hours': 730, 'Max_capacity_%':1.},
           'F2' : {'production' : 500 , 'hours': 730, 'Max_capacity_%':1.},
           'F3' : {'production' : 800,  'hours': 730, 'Max_capacity_%':1.},
           'F4' : {'production' : 1500, 'hours': 730, 'Max_capacity_%':1.},
           'F5' : {'production' : 300 , 'hours': 730, 'Max_capacity_%':1.}
           }


P = products.keys()
F = factory.keys()

# create model
model = ConcreteModel()

# Variables
model.x = Var(P,F, domain = NonNegativeIntegers)

# Objective
model.profit = Objective(expr = sum(sum(model.x[p,f]*products[p]['ACR'] for p in P)for f in F), 
                         sense = maximize)

model.cons = ConstraintList()
# Produciton constraint
for p in P:
    for f in F:
      model.cons.add(model.x[p,f] <= products[p]['demand'])

for f in F:
    model.cons.add(sum(model.x[p,f] for p in P) <=  factory[f]['Max_capacity_%']*factory[f]['production'])
    model.cons.add(sum(model.x[p,f]*products[p]['labor'] for p in P) <= factory[f]['hours'])

# solve
results = SolverFactory('glpk').solve(model)
results.write()
if results.solver.status:
    model.pprint()

# display solution

print(f'\nProfit = ${model.profit()}')
print('\nDecision Variables')

hours_working = dict()
capacity = dict()
for f in F:
    capacity[f] = 100*sum(model.x[p,f]() for p in P)/factory[f]['production']
    hours_working[f] = sum(model.x[p,f]()*products[p]['labor'] for p in P)
    h = 100*hours_working[f]/factory[f]['hours']

results = pd.DataFrame()
for f in F:
    results.loc[f,'Production'] = sum(model.x[p,f]() for p in P)
    results.loc[f,'% Capacity'] = capacity[f]
    results.loc[f,'Working hours'] = hours_working[f]
    results.loc[f,'% Hours'] = 100*hours_working[f]/factory[f]['hours']
    for p in P:
        results.loc[f,p] = model.x[p,f]()
    for p in P:
        results.loc[f,f'% demand {p}'] = 100*model.x[p,f]()/products[p]['demand']
    for p in P:
        results.loc[f,f'profit {p}'] = model.x[p,f]()*products[p]['ACR']

results.to_excel('Factory.xlsx')