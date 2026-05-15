# The Torchbearer

**Student Name:** Issa Alwazir
**Student ID:** 131040114
**Course:** CS 460 – Algorithms | Spring 2026

> This README is your project documentation. Write it the way a developer would document
> their design decisions , bullet points, brief justifications, and concrete examples where
> required. You are not writing an essay. You are explaining what you built and why you built
> it that way. Delete all blockquotes like this one before submitting.

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

> Document your understanding of why Dijkstra produces correct distances.
> Bullet points and short sentences throughout. No paragraphs.

### Part 3a: What the Invariant Means

- **For nodes already finalized (in S):**
  Nodes in the finalized set have been permanently assigned their true shortest-path distance from the source, and this distance will never change because Dijkstra selects the minimum-distance unfinalized node, ensuring no future path can be shorter.

- **For nodes not yet finalized (not in S):**
  Non-finalized nodes hold the best distance estimate found so far via paths whose intermediate vertices are all already finalized, but they may be improved by future relaxations.

### Part 3b: Why Each Phase Holds

- **Initialization:** Before any iteration, the source node has distance 0 (which is correct since the shortest path from source to itself is 0) and is marked as finalized, while all other nodes have distance infinity (the weakest upper bound), satisfying the invariant.

- **Maintenance:** At each iteration, I finalize the unfinalized node with minimum distance. Because all edge weights are nonnegative, any path to this node through unfinalized nodes would have cost at least the current minimum distance, so the invariant is preserved when this node joins S, and all edges from it are then safely relaxed.

- **Termination:** When all nodes have been finalized, the invariant guarantees that every node's distance value is the true shortest-path distance from the source, since every reachable node has been added to S and every unreachable node correctly remains at infinity.

### Part 3c: Why This Matters for the Route Planner

Correct shortest-path distances ensure that I can reliably calculate the true cost of any relic-visit sequence and make optimal routing decisions without wasting torch fuel on sub-optimal paths.

---

## Part 4: Search Design

### Why Greedy Fails

- **The failure mode:** A greedy algorithm that always visits the nearest unvisited relic next makes locally optimal choices that do not guarantee globally optimal total cost, because visiting a far relic first might unlock much cheaper paths to other relics.

- **Counter-example setup:** Using the spec illustration but with modified costs: S has relic neighbors B (cost 1) and C (cost 2); B connects to D (cost 1) and T (cost 1); C connects to B (cost 1), T (cost 1); D connects to B (cost 1), C (cost 1), and T (cost 50); all relics B, C, D must be visited.

- **What greedy picks:** Greedy starts at S, picks nearest relic B (cost 1), then picks nearest unvisited D (cost 1), then reaches C (cost 1), then exits at T. But D→T costs 50, so greedy pays: 1+1+1+50 = 53.

- **What optimal picks:** The optimal order avoids that expensive D→T edge. Optimal: S→C (cost 2)→B (cost 1)→D (cost 1)→C (cost 1)→T (cost 1) = 6 total. Or better: S→B→C→(back if needed)→T avoids the 50-cost edge. The key is reordering lets us use cheaper exits.

- **Why greedy loses:** Greedy locks into visiting D early because it's closest, then gets stuck with a 50-cost exit. A smarter order visits the relics such that the final exit from a cheap node, saving 47 fuel total.

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

- DystopiaQuest. "Dijkstra's Shortest Path Algorithm Visually Explained | How it Works | With Examples." YouTube video. https://www.youtube.com/watch?v=_ydLY-QBZRQ
- Course lecture notes on Dijkstra's algorithm and branch-and-bound search.
