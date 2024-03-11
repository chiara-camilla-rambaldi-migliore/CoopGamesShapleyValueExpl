from ortools.linear_solver import pywraplp
import itertools
import math


def LinearProgrammingExample(setup):
    """Linear programming sample."""
    # Instantiate a Glop solver, naming it LinearExample.
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if not solver:
        return

    x = {f"x_{n}_{m}": solver.IntVar(0, 1, f"x_{n}_{m}") for n in range(6) for m in range(3)}

    #print("Number of variables =", solver.NumVariables())

    # m for jobs
    # n for workers
    ct_1 = {f"ct_1_{n}": solver.Constraint(1, 1, f"ct_1_{n}") for n in range(6)}
    ct_2 = {f"ct_2_{m}": (solver.Constraint(-solver.infinity(), 2, f"ct_2_{m}") if setup[m] == 1 else None) for m in range(3)}

    for n in range(6):
        for m in range(3):
            ct_1[f"ct_1_{n}"].SetCoefficient(x[f"x_{n}_{m}"], 1)
            if ct_2[f"ct_2_{m}"] is not None:
                ct_2[f"ct_2_{m}"].SetCoefficient(x[f"x_{n}_{m}"], 1)

    ct_3 = {f"ct_3_{i}": (solver.Constraint(1, 1, f"ct_3_{i}") if setup[i+3]==1 else None) for i in range(3)}
    for i in range(3):
        for k in range(0, 2):
            if ct_3[f"ct_3_{i}"] is not None:
                ct_3[f"ct_3_{i}"].SetCoefficient(x[f"x_{2*i+k}_{i}"], 1)

    #print("Number of constraints =", solver.NumConstraints())

    # Objective function
    objective = solver.Objective()

    p = [{} for _ in range(3)]
    p[0]["j_0"] = 3
    p[0]["j_1"] = 1
    p[0]["j_2"] = 1

    p[1]["j_0"] = 1
    p[1]["j_1"] = 3
    p[1]["j_2"] = 1

    p[2]["j_0"] = 1
    p[2]["j_1"] = 1
    p[2]["j_2"] = 3


    p[0]["w_0"] = setup[6][0]
    p[0]["w_1"] = setup[7][0]
    p[0]["w_2"] = setup[8][0]
    p[0]["w_3"] = setup[9][0]
    p[0]["w_4"] = setup[10][0]
    p[0]["w_5"] = setup[11][0]

    p[1]["w_0"] = setup[6][1]
    p[1]["w_1"] = setup[7][1]
    p[1]["w_2"] = setup[8][1]
    p[1]["w_3"] = setup[9][1]
    p[1]["w_4"] = setup[10][1]
    p[1]["w_5"] = setup[11][1]

    p[2]["w_0"] = setup[6][2]
    p[2]["w_1"] = setup[7][2]
    p[2]["w_2"] = setup[8][2]
    p[2]["w_3"] = setup[9][2]
    p[2]["w_4"] = setup[10][2]
    p[2]["w_5"] = setup[11][2]

    for n in range(6):
        for m in range(3):
            objective.SetCoefficient(x[f"x_{n}_{m}"], sum([p[o][f"j_{m}"]*p[o][f"w_{n}"] for o in range(3)]))
            
        #print([objective.GetCoefficient(x[f"x_{n}_{m}"]) for m in range(3)])

    objective.SetMaximization()

    # Solve the system.
    #print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        # print("Solution:")
        # print(f"Objective value = {solver.Objective().Value():0.1f}")
        # for n in range(6):
        #     print(f"Worker {n+1}", end=": ")
        #     print([f"{x[f'x_{n}_{m}'].solution_value():0.1f}" for m in range(3)])
        
        return {f'x_{n}_{m}': x[f'x_{n}_{m}'].solution_value() for n in range(6) for m in range(3)}
    else:
        print("The problem does not have an optimal solution.")
        return None

    # print("\nAdvanced usage:")
    # print(f"Problem solved in {solver.wall_time():d} milliseconds")
    # print(f"Problem solved in {solver.iterations():d} iterations")
    

# LinearProgrammingExample()

def getPlayers1():
    D = [
        1,1,1,
        1,1,1,
        [1, 3, 1],
        [1, 1, 2],
        [3, 1, 2],
        [1, 2, 1],
        [1, 1, 2],
        [2, 3, 1]
    ]
    
    mean = [sum([d[i] for d in D[6:]])/len(D[6:]) for i in range(3)]

    R = [
        0,0,0,
        0,0,0,
        mean,
        mean,
        mean,
        mean,
        mean,
        mean
    ]

    return R, D

def getPlayers2():
    D = [
        1,1,1,
        1,1,1,
        [2, 4, 1],
        [2, 1, 3],
        [1, 3, 2],
        [0, 3, 1],
        [2, 1, 2],
        [0, 4, 1]
    ]

    mean = [sum([d[i] for d in D[6:]])/len(D[6:]) for i in range(3)]

    R = [
        0,0,0,
        0,0,0,
        mean,
        mean,
        mean,
        mean,
        mean,
        mean
    ]

    return R, D

def computeProfit(result):
    return result[f'x_{0}_{0}']

def computeShapley(games, p):
    count = 0
    len_d = 12
    sh = 0
    profit_with = 0
    for g in games:
        S = g[0]
        if S[p] == '0':
            S_with_p = S[:p] + '1' + S[p+1:]
            for g_ in games:
                if g_[0] == S_with_p:
                    profit_with = g_[1]
                    break
            profit_without = g[1]
            len_S = sum([int(d) for d in S])
            #optimization
            #do not calc fact if then it will multiplied by 0
            if(profit_with!=profit_without):
                tmp = math.factorial(len_S)*math.factorial(len_d-len_S-1)
                tmp /= math.factorial(len_d)
                tmp *= (profit_with-profit_without)
                sh += tmp
            count += 1
    return sh

def getShapleyValues(players):
    games = []
    for d in range(2**12):
        setup = []
        bin_d = f'{d:012b}'
        for i in range(len(bin_d)):
            setup.append(players[int(bin_d[i])][i])
        result = LinearProgrammingExample(setup)
        profit = computeProfit(result)
        games.append([bin_d, profit])

    for p in range(len(players[1])):
        sh = computeShapley(games, p)
        text = ["B_c2_j1", "B_c2_j2", "B_c2_j3", "B_c3_j1", "B_c3_j2", "B_c3_j3", "P_w1", "P_w2", "P_w3", "P_w4", "P_w5", "P_w6"]
        print(f"Shapley value for player {text[p]} is {sh}")


print("Shapley values for players problem 1")
players1 = getPlayers1()
getShapleyValues(players1)

# print("Shapley values for players problem 2")
# players2 = getPlayers2()
# getShapleyValues(players2)