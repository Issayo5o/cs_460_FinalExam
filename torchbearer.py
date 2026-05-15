"""
CS 460 – Algorithms: Final Programming Assignment
The Torchbearer

Student Name: ___________________________
Student ID:   ___________________________

INSTRUCTIONS
------------
- Implement every function marked TODO.
- Do not change any function signature.
- Do not remove or rename required functions.
- You may add helper functions.
- Variable names in your code must match what you define in README Part 5a.
- The pruning safety comment inside _explore() is graded. Do not skip it.

Submit this file as: torchbearer.py
"""

import heapq


# =============================================================================
# PART 1
# =============================================================================

def explain_problem():
    """
    Returns
    -------
    str
        Your Part 1 README answers, written as a string.
        Must match what you wrote in README Part 1.

    TODO
    """
    return """
- A single shortest-path run from S computes the cheapest way to reach each location, but cannot decide which relic to collect first; greedy choices about order do not guarantee global optimality.

- After knowing all inter-location travel costs, the structural decision that remains is the order in which to visit the relic chambers—a sequence problem where different orders incur different total costs despite using the same precomputed paths.

- This problem is a search over orders because the optimal solution depends on the sequence in which relics are visited, not just the shortest paths between them.
"""


# =============================================================================
# PART 2
# =============================================================================

def select_sources(spawn, relics, exit_node):
    """
    Parameters
    ----------
    spawn : node
    relics : list[node]
    exit_node : node

    Returns
    -------
    list[node]
        No duplicates. Order does not matter.

    TODO
    """
    sources = set([spawn, exit_node])
    sources.update(relics)
    return list(sources)


def run_dijkstra(graph, source):
    """
    Parameters
    ----------
    graph : dict[node, list[tuple[node, int]]]
        graph[u] = [(v, cost), ...]. All costs are nonnegative integers.
    source : node

    Returns
    -------
    dict[node, float]
        Minimum cost from source to every node in graph.
        Unreachable nodes map to float('inf').

    TODO
    """
    # Initialize distances
    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    
    # Priority queue: (distance, node)
    pq = [(0, source)]
    visited = set()
    
    while pq:
        d, u = heapq.heappop(pq)
        
        # Skip if already visited (already have optimal distance)
        if u in visited:
            continue
        
        visited.add(u)
        
        # Relax edges from u
        if u in graph:
            for v, cost in graph[u]:
                if v not in visited and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    heapq.heappush(pq, (dist[v], v))
    
    return dist


def precompute_distances(graph, spawn, relics, exit_node):
    """
    Parameters
    ----------
    graph : dict[node, list[tuple[node, int]]]
    spawn : node
    relics : list[node]
    exit_node : node

    Returns
    -------
    dict[node, dict[node, float]]
        Nested structure supporting dist_table[u][v] lookups
        for every source u your design requires.

    TODO
    """
    sources = select_sources(spawn, relics, exit_node)
    dist_table = {}
    
    for source in sources:
        dist_table[source] = run_dijkstra(graph, source)
    
    return dist_table


# =============================================================================
# PART 3
# =============================================================================

def dijkstra_invariant_check():
    """
    Returns
    -------
    str
        Your Part 3 README answers, written as a string.
        Must match what you wrote in README Part 3.

    TODO
    """
    return """
### Part 3a: Invariant Explanation

- **For nodes already finalized (in S):** Nodes in the finalized set have been permanently assigned their true shortest-path distance from the source, and this distance will never change because Dijkstra selects the minimum-distance unfinalized node, ensuring no future path can be shorter.

- **For nodes not yet finalized (not in S):** Non-finalized nodes hold the best distance estimate found so far via paths whose intermediate vertices are all already finalized, but they may be improved by future relaxations.

### Part 3b: Invariant Maintenance

- **Initialization:** Before the first iteration, the source node is initialized with distance 0 (the only correct distance) and placed in the priority queue, while all other nodes start with distance infinity and remain unfinalized. The invariant holds because no nodes have been finalized yet (S is empty), so the second part of the invariant is vacuously true.

- **Maintenance:** At each iteration, I pop the minimum-distance unfinalized node and finalize it. Because all edge weights are nonnegative, any path to this node through unfinalized nodes would have cost at least the current minimum distance, so finalizing it is safe. The invariant is preserved when this node joins S, and all edges from it are then relaxed.

- **Termination:** When the priority queue empties, all reachable nodes have been finalized, and their distance values are the true shortest-path distances from the source. Unreachable nodes remain at infinity.

### Part 3c: Why This Matters for the Route Planner

Correct shortest-path distances ensure that I can reliably calculate the true cost of any relic-visit sequence and make optimal routing decisions without wasting torch fuel on sub-optimal paths.
"""


# =============================================================================
# PART 4
# =============================================================================

def explain_search():
    """
    Returns
    -------
    str
        Your Part 4 README answers, written as a string.
        Must match what you wrote in README Part 4.

    TODO
    """
    return """
### Why Greedy Fails

- **The failure mode:** A greedy algorithm that always visits the nearest unvisited relic next makes locally optimal choices that do not guarantee globally optimal total cost, because visiting a far relic first might unlock much cheaper paths to other relics.

- **Counter-example setup:** Consider a simple graph: S connects to both B (cost 10) and C (cost 1); B is a relic; C is also a relic; and B connects directly to the exit T (cost 1), while C connects to T with cost 100.

- **What greedy picks:** Greedy starts at S, picks the nearest relic C (cost 1), then tries to reach T from C. But T is only reachable from B, so greedy is stuck. Alternatively, if both relics have viable exits, greedy picks C first (cost 1), then later realizes B had the cheap exit (cost 1), so greedy pays 1+100+? instead of the smart order.

- **What optimal picks:** The optimal order is S -> B (cost 10) -> C (cost ?) -> T (cost 1 from B). By visiting B first despite its higher initial cost, we unlock the cheap B -> T edge, saving fuel overall.

- **Why greedy loses:** Greedy picks by proximity alone, ignoring that a seemingly distant relic might have cheaper outgoing edges or connections. Different relic orders can dramatically change which exits are available and their costs.

### What the Algorithm Must Explore

- I must explore different orders in which to visit relics, because the total fuel cost depends critically on the sequence, and no greedy choice of "which relic next" guarantees that the resulting order is globally optimal.
"""


# =============================================================================
# PARTS 5 + 6
# =============================================================================

def find_optimal_route(dist_table, spawn, relics, exit_node):
    """
    Parameters
    ----------
    dist_table : dict[node, dict[node, float]]
        Output of precompute_distances.
    spawn : node
    relics : list[node]
        Every node in this list must be visited at least once.
    exit_node : node
        The route must end here.

    Returns
    -------
    tuple[float, list[node]]
        (minimum_fuel_cost, ordered_relic_list)
        Returns (float('inf'), []) if no valid route exists.

    TODO
    """
    # Convert relics to a set for O(1) membership testing
    relics_remaining = set(relics)
    
    # best = [best_cost, best_order]
    best = [float('inf'), []]
    
    # Start the search from spawn with no relics collected yet
    _explore(dist_table, spawn, relics_remaining, [], 0, exit_node, best)
    
    return (best[0], best[1])


def _explore(dist_table, current_loc, relics_remaining, relics_visited_order,
             cost_so_far, exit_node, best):
    """
    Recursive helper for find_optimal_route.

    Parameters
    ----------
    dist_table : dict[node, dict[node, float]]
    current_loc : node
    relics_remaining : collection
        Your chosen data structure from README Part 5b.
    relics_visited_order : list[node]
    cost_so_far : float
    exit_node : node
    best : list
        Mutable container for the best solution found so far.

    Returns
    -------
    None
        Updates best in place.

    TODO
    Implement: base case, pruning, recursive case, backtracking.

    REQUIRED: Add a 1-2 sentence comment near your pruning condition
    explaining why it is safe (cannot skip the optimal solution).
    This comment is graded.
    """
    # Base case: no relics left to visit
    if not relics_remaining:
        # Try to reach the exit from current location
        if current_loc in dist_table and exit_node in dist_table[current_loc]:
            cost_to_exit = dist_table[current_loc][exit_node]
            if cost_to_exit != float('inf'):
                total_cost = cost_so_far + cost_to_exit
                # Update best if this is better
                if total_cost < best[0]:
                    best[0] = total_cost
                    best[1] = list(relics_visited_order)
        return
    
    # Check if we can possibly reach the exit from here
    if current_loc not in dist_table or exit_node not in dist_table[current_loc]:
        return
    
    # Lower bound: cost so far + direct path to exit (ignoring remaining relics)
    cost_to_exit = dist_table[current_loc][exit_node]
    lower_bound = cost_so_far + cost_to_exit
    
    # Pruning: if lower bound already beats best, stop exploring this branch.
    # This is safe because even if we visit all remaining relics perfectly,
    # we cannot do better than this lower bound, so this path has no hope of being optimal.
    if lower_bound >= best[0]:
        return
    
    # Try visiting each remaining relic
    for relic in list(relics_remaining):
        if current_loc not in dist_table or relic not in dist_table[current_loc]:
            continue
        
        cost_to_relic = dist_table[current_loc][relic]
        if cost_to_relic == float('inf'):
            continue
        
        # Recurse: visit this relic next
        new_relics = relics_remaining - {relic}
        new_cost = cost_so_far + cost_to_relic
        new_order = relics_visited_order + [relic]
        
        _explore(dist_table, relic, new_relics, new_order, new_cost, exit_node, best)


# =============================================================================
# PIPELINE
# =============================================================================

def solve(graph, spawn, relics, exit_node):
    """
    Parameters
    ----------
    graph : dict[node, list[tuple[node, int]]]
    spawn : node
    relics : list[node]
    exit_node : node

    Returns
    -------
    tuple[float, list[node]]
        (minimum_fuel_cost, ordered_relic_list)
        Returns (float('inf'), []) if no valid route exists.

    TODO
    """
    # First, compute shortest paths from all important nodes
    dist_table = precompute_distances(graph, spawn, relics, exit_node)
    
    # Then, search for the best order to visit relics
    return find_optimal_route(dist_table, spawn, relics, exit_node)


# =============================================================================
# PROVIDED TESTS (do not modify)
# Graders will run additional tests beyond these.
# =============================================================================

def _run_tests():
    print("Running provided tests...")

    # Test 1: Spec illustration. Optimal cost = 4.
    graph_1 = {
        'S': [('B', 1), ('C', 2), ('D', 2)],
        'B': [('D', 1), ('T', 1)],
        'C': [('B', 1), ('T', 1)],
        'D': [('B', 1), ('C', 1)],
        'T': []
    }
    cost, order = solve(graph_1, 'S', ['B', 'C', 'D'], 'T')
    assert cost == 4, f"Test 1 FAILED: expected 4, got {cost}"
    print(f"  Test 1 passed  cost={cost}  order={order}")

    # Test 2: Single relic. Optimal cost = 5.
    graph_2 = {
        'S': [('R', 3)],
        'R': [('T', 2)],
        'T': []
    }
    cost, order = solve(graph_2, 'S', ['R'], 'T')
    assert cost == 5, f"Test 2 FAILED: expected 5, got {cost}"
    print(f"  Test 2 passed  cost={cost}  order={order}")

    # Test 3: No valid path to exit. Must return (inf, []).
    graph_3 = {
        'S': [('R', 1)],
        'R': [],
        'T': []
    }
    cost, order = solve(graph_3, 'S', ['R'], 'T')
    assert cost == float('inf'), f"Test 3 FAILED: expected inf, got {cost}"
    print(f"  Test 3 passed  cost={cost}")

    # Test 4: Relics reachable only through intermediate rooms.
    # Optimal cost = 6.
    graph_4 = {
        'S': [('X', 1)],
        'X': [('R1', 2), ('R2', 5)],
        'R1': [('Y', 1)],
        'Y': [('R2', 1)],
        'R2': [('T', 1)],
        'T': []
    }
    cost, order = solve(graph_4, 'S', ['R1', 'R2'], 'T')
    assert cost == 6, f"Test 4 FAILED: expected 6, got {cost}"
    print(f"  Test 4 passed  cost={cost}  order={order}")

    # Test 5: Explanation functions must return non-placeholder strings.
    for fn in [explain_problem, dijkstra_invariant_check, explain_search]:
        result = fn()
        assert isinstance(result, str) and result != "TODO" and len(result) > 20, \
            f"Test 5 FAILED: {fn.__name__} returned placeholder or empty string"
    print("  Test 5 passed  explanation functions are non-empty")

    print("\nAll provided tests passed.")


if __name__ == "__main__":
    _run_tests()
