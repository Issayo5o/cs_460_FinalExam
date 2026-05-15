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
### Part 3a: What the Invariant Means

- **For nodes already finalized (in S):** Nodes in the finalized set have been permanently assigned their true shortest-path distance from the source, and this distance will never change because Dijkstra selects the minimum-distance unfinalized node, ensuring no future path can be shorter.

- **For nodes not yet finalized (not in S):** Non-finalized nodes hold the best distance estimate found so far via paths whose intermediate vertices are all already finalized, but they may be improved by future relaxations.

### Part 3b: Why Each Phase Holds

- **Initialization: why the invariant holds before iteration 1:** Before any iteration, the source node has distance 0 (which is correct since the shortest path from source to itself is 0) and is marked as finalized, while all other nodes have distance infinity (the weakest upper bound), satisfying the invariant.

- **Maintenance: why finalizing the min-dist node is always correct:** At each iteration, I finalize the unfinalized node with minimum distance. Because all edge weights are nonnegative, any path to this node through unfinalized nodes would have cost at least the current minimum distance, so the invariant is preserved when this node joins S, and all edges from it are then safely relaxed.

- **Termination: what the invariant guarantees when the algorithm ends:** When all nodes have been finalized, the invariant guarantees that every node's distance value is the true shortest-path distance from the source, since every reachable node has been added to S and every unreachable node correctly remains at infinity.

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

- **Counter-example setup:** Using the spec illustration: S has relic neighbors B (cost 1) and C (cost 2); B connects to D (cost 1) and T (cost 1); C connects to T (cost 1); D connects to B (cost 1), C (cost 1), and T (cost 100); all relics B, C, D must be visited.

- **What greedy picks:** Greedy starts at S and greedily picks the nearest relic B (cost 1), then from B picks nearest unvisited D (cost 1), then from D picks nearest unvisited C (cost 1), finally reaches T (cost 1), for a total of 1+1+1+1 = 4.

- **What optimal picks:** The optimal order is S → B (1) → D (1) → C (1) → T (1), also totaling 4, but consider if T from D had cost 50 instead: greedy would waste fuel on that bad path, while reordering to S → C → B → D → T might find T from C is cheaper and save fuel overall.

- **Why greedy loses:** Greedy's inability to look ahead means it cannot see that routing through intermediate relics in a different sequence might connect to cheaper exit paths, missing reorderings that reduce total cost by finding shared cheap intermediate nodes.

### What the Algorithm Must Explore

- The algorithm must explore different orders in which to visit relics, because the total fuel cost depends critically on the sequence, and no greedy choice of "which relic next" guarantees that the resulting order is globally optimal.
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
    pass


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
    pass


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
    pass


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
