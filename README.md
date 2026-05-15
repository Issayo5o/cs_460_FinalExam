# The Torchbearer

**Student Name:** Issa Alwazir
**Student ID:** 131040114
**Course:** CS 460 – Algorithms | Spring 2026

---

## Part 1: Problem Analysis

- **Why a single shortest-path run from S is not enough:**
  A single shortest-path run from S computes the cheapest way to reach each location, but cannot decide which relic to collect first; greedy choices about order do not guarantee global optimality.

- **What decision remains after all inter-location costs are known:**
  After knowing all inter-location travel costs, the structural decision that remains is the order in which to visit the relic chambers—a sequence problem where different orders incur different total costs despite using the same precomputed paths.

- **Why this requires a search over orders (one sentence):**
  This problem is a search over orders because the optimal solution depends on the sequence in which relics are visited, not just the shortest paths between them.

---

## Part 2: Precomputation Design

### Part 2a: Source Selection

| Source Node Type | Why it is a source |
|---|---|
| Spawn (entrance) | I need to run Dijkstra from spawn to compute distances to all relics and the exit; this is the starting point of every route. |
| Relic chambers | I need to run Dijkstra from each relic to compute distances to all other relics and to the exit; the search needs these distances to explore different visitation orders. |
| Exit node | I include the exit node, although the primary need is distances FROM relics and spawn TO the exit; running from exit provides consistent distance lookups. |

### Part 2b: Distance Storage

| Property | Your answer |
|---|---|
| Data structure name | Nested dictionary: dict[node, dict[node, float]] |
| What the keys represent | Outer keys are source nodes; inner keys are destination nodes. |
| What the values represent | The float values are the minimum cost (shortest-path distance) from the outer-key source to the inner-key destination. |
| Lookup time complexity | O(1) average case for dictionary lookups. |
| Why O(1) lookup is possible | Python dictionaries use hash tables internally, enabling constant-time average-case access by key. |

### Part 2c: Precomputation Complexity

- **Number of Dijkstra runs:** k + 2, where k = |M| (one run per relic, plus one from spawn and one from exit).
- **Cost per run:** O((|V| + |E|) log |V|) using binary heap; single shortest-path run costs O(m log n).
- **Total complexity:** O((k + 2) * (m log n)) = O(k * m log n) (dropping lower-order terms).
- **Justification (one line):** I must compute shortest paths from every critical node (relics, spawn, exit), and each Dijkstra run provides those one source at a time.

---

## Part 3: Algorithm Correctness

### Part 3a: Invariant Explanation

- **For nodes already finalized (in S):**
  Nodes in the finalized set have been permanently assigned their true shortest-path distance from the source, and this distance will never change because Dijkstra selects the minimum-distance unfinalized node, ensuring no future path can be shorter.

- **For nodes not yet finalized (not in S):**
  Non-finalized nodes hold the best distance estimate found so far via paths whose intermediate vertices are all already finalized, but they may be improved by future relaxations.

### Part 3b: Invariant Maintenance

- **Initialization:** Before the first iteration, the source node is initialized with distance 0 (the only correct distance) and placed in the priority queue, while all other nodes start with distance infinity and remain unfinalized. The invariant holds because no nodes have been finalized yet (S is empty), so the second part of the invariant is vacuously true.

- **Maintenance:** At each iteration, I pop the minimum-distance unfinalized node and finalize it. Because all edge weights are nonnegative, any path to this node through unfinalized nodes would have cost at least the current minimum distance, so finalizing it is safe. The invariant is preserved when this node joins S, and all edges from it are then relaxed.

- **Termination:** When the priority queue empties, all reachable nodes have been finalized, and their distance values are the true shortest-path distances from the source. Unreachable nodes remain at infinity.

### Part 3c: Why This Matters for the Route Planner

Correct shortest-path distances ensure that I can reliably calculate the true cost of any relic-visit sequence and make optimal routing decisions without wasting torch fuel on sub-optimal paths.

---

## Part 4: Search Design

### Why Greedy Fails

- **The failure mode:** A greedy algorithm that always visits the nearest unvisited relic next makes locally optimal choices that do not guarantee globally optimal total cost, because visiting a far relic first might unlock much cheaper paths to other relics.

- **Counter-example setup:** Consider a simple graph: S connects to both B (cost 10) and C (cost 1); B is a relic; C is also a relic; and B connects directly to the exit T (cost 1), while C connects to T with cost 100.

- **What greedy picks:** Greedy starts at S, picks the nearest relic C (cost 1), then tries to reach T from C. But T is only reachable from B, so greedy is stuck. Alternatively, if both relics have viable exits, greedy picks C first (cost 1), then later realizes B had the cheap exit (cost 1), so greedy pays 1+100+? instead of the smart order.

- **What optimal picks:** The optimal order is S -> B (cost 10) -> C (cost ?) -> T (cost 1 from B). By visiting B first despite its higher initial cost, we unlock the cheap B -> T edge, saving fuel overall.

- **Why greedy loses:** Greedy picks by proximity alone, ignoring that a seemingly distant relic might have cheaper outgoing edges or connections. Different relic orders can dramatically change which exits are available and their costs.

### What the Algorithm Must Explore

- I must explore different orders in which to visit relics, because the total fuel cost depends critically on the sequence, and no greedy choice of "which relic next" guarantees that the resulting order is globally optimal.

---

## Part 5: State and Search Space

### Part 5a: State Representation

| Component | Variable name in code | Data type | Description |
|---|---|---|---|
| Current location | current_loc | node | The dungeon chamber where the Torchbearer is currently positioned. |
| Relics already collected | relics_remaining | set | A set of relics not yet visited; I track what remains rather than what I have visited. |
| Fuel cost so far | cost_so_far | float | The cumulative distance (torch fuel) spent from spawn to the current location. |

### Part 5b: Data Structure for Visited Relics

| Property | Your answer |
|---|---|
| Data structure chosen | Set (Python set type) |
| Operation: check if relic already collected | Time complexity: O(1) average case (hash table lookup) |
| Operation: mark a relic as collected | Time complexity: O(1) average case (set.remove after copying) |
| Operation: unmark a relic (backtrack) | Time complexity: O(1) average case (set union/difference creates new set via recursion unwinding) |
| Why this structure fits | Sets provide O(1) average membership testing and efficient set operations (union, difference) needed during recursive search and backtracking. |

### Part 5c: Worst-Case Search Space

- **Worst-case number of orders considered:** O(k!) where k = |M| (factorial because the search tree explores all permutations of relics).
- **Why:** The recursive search has k choices for which relic to visit first, k-1 for the second, and so on, yielding k! total orderings in the worst case when pruning cannot eliminate branches.

---

## Part 6: Pruning

### Part 6a: Best-So-Far Tracking

- **What is tracked:** I keep track of the best (lowest cost) complete solution I've found so far, along with the order of relics I visited to get that cost.

- **When it is used:** Before I explore a new branch in the search tree, I check if there's any way it could possibly beat the best solution I already have.

- **What it allows the algorithm to skip:** If a branch can't beat the best solution, I skip exploring it entirely. This cuts down the search tree a lot.

### Part 6b: Lower Bound Estimation

- **What information is available at the current state:** I know where I am right now, how much fuel I've spent getting here, and which relics I still need to collect.

- **What the lower bound accounts for:** I calculate the minimum possible remaining cost: the cost from my current location straight to the exit, ignoring that I haven't visited the remaining relics yet.

- **Why it never overestimates:** This bound assumes I can teleport past all the relics I haven't collected, which is impossible. So the real cost must be at least this high—the bound is always a floor.

### Part 6c: Pruning Correctness

- **Why pruning is safe:** If the lower bound (cost so far + direct path to exit) is already bigger than or equal to my best solution, then there's no way any complete path through this branch can beat the best. So I can safely prune the branch without ever risking losing the optimal solution.

- **Why we don't lose the optimal:** The optimal solution will always be in some unpruned branch, because its lower bound must be less than itself, so it won't get pruned away.

---

## References

- DystopiaQuest. "Dijkstra's Shortest Path Algorithm Visually Explained | How it Works | With Examples." YouTube video. https://www.youtube.com/watch?v=CmIQ29cUGiE&time_continue=74&embeds_referring_euri=https%3A%2F%2Fsdsu.instructure.com%2F 
- Course lecture notes on Dijkstra's algorithm and branch-and-bound search.
