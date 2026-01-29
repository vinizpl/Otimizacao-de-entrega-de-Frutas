from ortools.linear_solver import pywraplp
import csv

clientes = []
with open('clientes.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        clientes.append({
            'id': int(row['id']),
            'investimento': float(row['investimento']),
            'taxa_deterioracao': float(row['taxa_deterioracao']),
            'distancias': [
                float(row['dist_c1']),
                float(row['dist_c2']),
                float(row['dist_c3']),
                float(row['dist_c4']),
                float(row['dist_c5'])
            ]
        })

n_clientes = len(clientes)
n_centros = 5  # (j ∈ {1,2,3,4,5})
n_caminhoes = 2

custos_caminhoes = [0.5, 0.7] 

solver = pywraplp.Solver.CreateSolver('SCIP')

Y = {}
for i in range(n_caminhoes):
    for j in range(n_centros):
        for k in range(n_clientes):
            Y[(i, j, k)] = solver.IntVar(0, 1, f'Y_{i}_{j}_{k}')

objective = solver.Objective()
for i in range(n_caminhoes):
    for j in range(n_centros):
        for k in range(n_clientes):
            objective.SetCoefficient(
                Y[(i, j, k)], 
                clientes[k]['taxa_deterioracao'] * clientes[k]['distancias'][j]
            )
objective.SetMinimization()

for k in range(n_clientes):
    constraint = solver.Constraint(1, 1)
    for i in range(n_caminhoes):
        for j in range(n_centros):  # j varia de 1 a 5
            constraint.SetCoefficient(Y[(i, j, k)], 1)

for k in range(n_clientes):
    constraint = solver.Constraint(0, clientes[k]['investimento'])
    for i in range(n_caminhoes):
        for j in range(n_centros):  # j varia de 1 a 5
            custo_transporte = custos_caminhoes[i] * clientes[k]['distancias'][j]
            constraint.SetCoefficient(Y[(i, j, k)], custo_transporte)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print('Solução ótima encontrada!')
    print(f'Valor objetivo (deterioração total mínima): {objective.Value()}')
    
    print('\nAlocação de clientes:')
    total_custo = 0
    for k in range(n_clientes):
        for i in range(n_caminhoes):
            for j in range(n_centros):
                if Y[(i, j, k)].solution_value() > 0.5:
                    custo = custos_caminhoes[i] * clientes[k]['distancias'][j]
                    deterioracao = clientes[k]['taxa_deterioracao'] * clientes[k]['distancias'][j]
                    print(f'Cliente {k+1} (Invest: {clientes[k]["investimento"]}) -> '
                          f'Caminhão {i+1} (R${custos_caminhoes[i]}/km), '
                          f'Centro {j+1} (Dist: {clientes[k]["distancias"][j]}km)')
                    print(f'  Custo transporte: R${custo:.2f}')
                    print(f'  Deterioração: {deterioracao:.2f}\n')
                    total_custo += custo
    
    print(f'Custo total de transporte: R${total_custo:.2f}')
else:
    print('Não foi encontrada solução ótima.')
