import copy
import numpy as np
import heapq

INF = float("inf")


class SubProblem:
    def __init__(self, node_id, matrix, lb, partial_tour, status="Aktywny"):
        self.id = node_id
        self.matrix = matrix
        self.lb = lb
        self.partial_tour = partial_tour
        self.status = status


def reduce_matrix(M):
    RM = copy.deepcopy(M).astype(float)
    lb = 0.0
    n = RM.shape[0]

    for i in range(n):
        finite = RM[i][np.isfinite(RM[i])]
        if finite.size > 0:
            row_min = finite.min()
            if row_min > 0:
                for j in range(n):
                    if RM[i][j] != INF:
                        RM[i][j] -= row_min
                lb += row_min

    for j in range(n):
        finite = RM[:, j][np.isfinite(RM[:, j])]
        if finite.size > 0:
            col_min = finite.min()
            if col_min > 0:
                for i in range(n):
                    if RM[i][j] != INF:
                        RM[i][j] -= col_min
                lb += col_min

    return lb, RM


def compute_penalties(matrix):
    n = matrix.shape[0]
    best_edge = None
    best_penalty = -1

    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 0:
                row_values = [
                    matrix[i][k]
                    for k in range(n)
                    if k != j and matrix[i][k] != INF
                ]

                col_values = [
                    matrix[k][j]
                    for k in range(n)
                    if k != i and matrix[k][j] != INF
                ]

                row_min = min(row_values) if row_values else 0
                col_min = min(col_values) if col_values else 0

                penalty = row_min + col_min

                if penalty > best_penalty:
                    best_penalty = penalty
                    best_edge = (i, j)

    return best_edge, best_penalty


def degrees_ok(edges, n):
    starts = [a for a, b in edges]
    ends = [b for a, b in edges]

    return len(starts) == len(set(starts)) and len(ends) == len(set(ends))


def creates_premature_cycle(edges, n):
    if len(edges) >= n:
        return False

    graph = {}

    for a, b in edges:
        graph[a] = b

    for start in graph:
        current = start
        visited = set()

        while current in graph:
            if current in visited:
                return True

            visited.add(current)
            current = graph[current]

            if current == start and len(edges) < n:
                return True

    return False


def is_full_cycle(edges, n):
    if len(edges) != n:
        return False

    if not degrees_ok(edges, n):
        return False

    graph = {}

    for a, b in edges:
        graph[a] = b

    start = edges[0][0]
    current = start
    visited = []

    for _ in range(n):
        if current in visited:
            return False

        if current not in graph:
            return False

        visited.append(current)
        current = graph[current]

    return current == start and len(set(visited)) == n


def block_subtours(matrix, edges, n):
    new_matrix = copy.deepcopy(matrix)

    graph = {}
    incoming = {}

    for a, b in edges:
        graph[a] = b
        incoming[b] = a

    starts = []

    for a, b in edges:
        if a not in incoming:
            starts.append(a)

    for start in starts:
        current = start
        visited = set()

        while current in graph and current not in visited:
            visited.add(current)
            current = graph[current]

        end = current

        if end != start and len(edges) < n - 1:
            new_matrix[end][start] = INF

    return new_matrix


def find_last_edge(edges, n):
    starts = {a for a, b in edges}
    ends = {b for a, b in edges}

    missing_start = [i for i in range(n) if i not in starts]
    missing_end = [i for i in range(n) if i not in ends]

    if len(missing_start) == 1 and len(missing_end) == 1:
        return missing_start[0], missing_end[0]

    return None


def calculate_real_cost(edges, cost_matrix):
    cost = 0

    for a, b in edges:
        cost += cost_matrix[a][b]

    return cost


def KZ0_podzial(pp_id, edge, penalty):
    print(f"KZ0: PP{pp_id} - podział względem krawędzi {edge}, kara = {penalty}")
    return "KZ0 - podział"


def KZ1_brak_rozwiazan(pp_id, reason):
    print(f"KZ1: PP{pp_id} - zamknięcie, {reason}")
    return "KZ1 - brak rozwiązań dopuszczalnych"


def KZ2_lb_gorsze_od_vstar(pp_id, lb, v_star):
    if lb >= v_star:
        print(f"KZ2: PP{pp_id} - zamknięcie, LB = {lb} >= v* = {v_star}")
        return True, "KZ2 - LB >= v*"

    return False, "Aktywny"


def KZ3_rozwiazanie_dopuszczalne(pp_id, edges, n, cost_matrix, v_star):
    if len(edges) == n - 1:
        last_edge = find_last_edge(edges, n)

        if last_edge is None:
            return False, v_star, None, "Aktywny"

        full_tour = edges + [last_edge]

        if not np.isfinite(cost_matrix[last_edge[0]][last_edge[1]]):
            return False, v_star, None, "Aktywny"

        if is_full_cycle(full_tour, n):
            real_cost = calculate_real_cost(full_tour, cost_matrix)

            print(f"KZ3: PP{pp_id} - znaleziono pełne rozwiązanie: {full_tour}")
            print(f"Koszt rzeczywisty = {real_cost}")

            if real_cost < v_star:
                print(f"Poprawa wartości odcinającej: v* = {v_star} -> {real_cost}")
                return True, real_cost, full_tour, "KZ3 - poprawa v*"

            return True, v_star, None, "KZ3 - bez poprawy v*"

    return False, v_star, None, "Aktywny"


def print_subproblem(pp):
    print("----------------------------------------")
    print(f"PP numer: {pp.id}")
    print(f"LB: {pp.lb}")
    print(f"KZ/status: {pp.status}")
    print(f"Częściowe rozwiązanie TSP: {pp.partial_tour}")
    print("Macierz zredukowana:")
    print(pp.matrix)
    print("----------------------------------------\n")


def create_left_subproblem(current, edge, node_counter, n):
    u, v = edge

    left_edges = current.partial_tour + [(u, v)]

    if not degrees_ok(left_edges, n):
        KZ1_brak_rozwiazan(node_counter, "naruszono stopnie wierzchołków")
        return None

    if creates_premature_cycle(left_edges, n):
        KZ1_brak_rozwiazan(node_counter, "powstał niedozwolony podcykl")
        return None

    left_matrix = copy.deepcopy(current.matrix)

    for k in range(n):
        left_matrix[u][k] = INF
        left_matrix[k][v] = INF

    left_matrix[v][u] = INF
    left_matrix = block_subtours(left_matrix, left_edges, n)

    reduction, left_matrix = reduce_matrix(left_matrix)
    left_lb = current.lb + reduction

    return SubProblem(
        node_id=node_counter,
        matrix=left_matrix,
        lb=left_lb,
        partial_tour=left_edges,
        status=f"Z krawędzią {edge}"
    )


def create_right_subproblem(current, edge, node_counter):
    u, v = edge

    right_matrix = copy.deepcopy(current.matrix)
    right_matrix[u][v] = INF

    reduction, right_matrix = reduce_matrix(right_matrix)
    right_lb = current.lb + reduction

    return SubProblem(
        node_id=node_counter,
        matrix=right_matrix,
        lb=right_lb,
        partial_tour=current.partial_tour.copy(),
        status=f"Bez krawędzi {edge}"
    )


def solve_tsp_little(cost_matrix):
    n = len(cost_matrix)

    node_counter = 0
    v_star = INF
    best_tour = None

    initial_reduction, initial_matrix = reduce_matrix(cost_matrix)

    root = SubProblem(
        node_id=node_counter,
        matrix=initial_matrix,
        lb=initial_reduction,
        partial_tour=[],
        status="Start"
    )

    queue = []
    heapq.heappush(queue, (root.lb, root.id, root))

    print("========================================")
    print("START ALGORYTMU LITTLE'A")
    print("Wartość odcinająca: v* = INF")
    print("========================================\n")

    while queue:
        _, _, current = heapq.heappop(queue)

        print_subproblem(current)

        zamknij, status = KZ2_lb_gorsze_od_vstar(
            current.id,
            current.lb,
            v_star
        )

        if zamknij:
            current.status = status
            continue

        zamknij, v_star, found_tour, status = KZ3_rozwiazanie_dopuszczalne(
            current.id,
            current.partial_tour,
            n,
            cost_matrix,
            v_star
        )

        if zamknij:
            current.status = status

            if found_tour is not None:
                best_tour = found_tour

            continue

        edge, penalty = compute_penalties(current.matrix)

        if edge is None:
            current.status = KZ1_brak_rozwiazan(
                current.id,
                "brak możliwego zera do podziału"
            )
            continue

        current.status = KZ0_podzial(current.id, edge, penalty)

        node_counter += 1
        left_node = create_left_subproblem(
            current,
            edge,
            node_counter,
            n
        )

        if left_node is not None:
            heapq.heappush(queue, (left_node.lb, left_node.id, left_node))
            print(f"Dodano PP{left_node.id}: {left_node.status}, LB = {left_node.lb}")

        node_counter += 1
        right_node = create_right_subproblem(
            current,
            edge,
            node_counter
        )

        heapq.heappush(queue, (right_node.lb, right_node.id, right_node))
        print(f"Dodano PP{right_node.id}: {right_node.status}, LB = {right_node.lb}\n")

    print("========================================")
    print("ROZWIĄZANIE OPTYMALNE")
    print("========================================")
    print(f"Najlepsza trasa P: {best_tour}")
    print(f"Wartość funkcji celu v*: {v_star}")

    return v_star, best_tour


def example_cost_matrix():
    return np.array([
        [INF, 10, 8, 9, 7, 14],
        [10, INF, 10, 5, 6, 9],
        [8, 10, INF, 8, 9, 10],
        [9, 5, 8, INF, 6, 8],
        [7, 6, 9, 6, INF, 5],
        [14, 9, 10, 8, 5, INF]
    ], dtype=float)