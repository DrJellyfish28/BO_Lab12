import copy
import numpy as np

INF = float('inf')

class SubProblem:
    def __init__(self, node_id, matrix, lb, partial_tour, status="Aktywny"):
        self.id = node_id
        self.matrix = matrix
        self.lb = lb
        self.partial_tour = partial_tour
        self.status = status

#TODO zaimplementować 

def reduce_matrix(M : np.ndarray):
    RM = np.zeros(M.shape)
    lb = 0
    for i in range(M.shape[0]):
        minim = INF
        for j in range(M.shape[1]):
            if M[i][j] < minim:
                minim = M[i][j]
        for j in range(M.shape[1]):
            RM[i][j] = M[i][j] - minim
        lb += minim

    for i in range(RM.shape[0]):
        minim = INF
        for j in range(RM.shape[1]):
            if RM[j][i] < minim:
                minim = RM[j][i]
        for j in range(RM.shape[1]):
            RM[j][i] = RM[j][i] - minim
        lb += minim

    return lb, RM

#TODO zaimpementować

def compute_penalties(matrix):

    best_edge = (0, 1)
    penalty = 0
    pass
    
    return best_edge, penalty

#TODO zaimplementować

def block_subtours(matrix, partial_tour, next_edge):

    new_matrix = copy.deepcopy(matrix)
    
    pass
    
    return new_matrix

def solve_tsp_little(cost_matrix):
    n = len(cost_matrix)
    node_counter = 0
    
    v_star = INF
    best_tour = None
    
    initial_cost, initial_matrix = reduce_matrix(cost_matrix)
    
    root = SubProblem(
        node_id=node_counter, 
        matrix=initial_matrix, 
        lb=initial_cost, 
        partial_tour=[]
    )
    
    subproblems_list = [root]
    
    print(f"--- START ALGORYTMU LITTLE'A ---")
    print(f"Początkowe LB (Korzeń): {root.lb}\n")

    while subproblems_list:
        current = subproblems_list.pop()
        
        print(f"Analiza Podproblemu {current.id} (LB={current.lb})")
        
        if current.lb >= v_star:
            current.status = "KZ2 - Obcięcie (LB >= v*)"
            print(f"  -> Zamknięto (KZ2): LB ({current.lb}) >= v* ({v_star})")
            continue

        if len(current.partial_tour) == n:
            if current.lb < v_star:
                v_star = current.lb
                best_tour = current.partial_tour
                current.status = "KZ3 - Znaleziono lepsze rozw."
                print(f"  *** NOWE NAJLEPSZE ROZWIĄZANIE (v* = {v_star}) ***")
            continue

        best_edge, penalty = compute_penalties(current.matrix)
        
        if best_edge is None:
            current.status = "KZ1 - Brak drogi dopuszczalnej"
            print("  -> Zamknięto (KZ1): Brak możliwości dalszego podziału.")
            continue
            
        u, v = best_edge
        current.status = "Rozgałęziony"
        print(f"  -> Rozgałęzianie na krawędzi {best_edge} (Kara: {penalty})")

        node_counter += 1
        left_matrix = copy.deepcopy(current.matrix)
        
        for k in range(n):
            left_matrix[u][k] = INF
            left_matrix[k][v] = INF
            
        left_tour = current.partial_tour + [(u, v)]
        left_matrix = block_subtours(left_matrix, left_tour, (u, v))
        
        left_reduction, left_matrix = reduce_matrix(left_matrix)
        left_lb = current.lb + left_reduction
        
        left_node = SubProblem(node_counter, left_matrix, left_lb, left_tour)

        node_counter += 1
        right_matrix = copy.deepcopy(current.matrix)
        right_matrix[u][v] = INF 
        
        right_reduction, right_matrix = reduce_matrix(right_matrix)
        right_lb = current.lb + right_reduction + penalty 
        
        right_node = SubProblem(node_counter, right_matrix, right_lb, current.partial_tour)

        subproblems_list.append(right_node)
        subproblems_list.append(left_node)
        
        print(f"     Dodano Podproblem {left_node.id} (Z krawędzią {best_edge}, LB={left_node.lb})")
        print(f"     Dodano Podproblem {right_node.id} (Bez krawędzi {best_edge}, LB={right_node.lb})")

    return v_star, best_tour