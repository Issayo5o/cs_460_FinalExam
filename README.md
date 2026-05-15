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

- **Initialization: why the invariant holds before iteration 1:**
  Before any iteration, the source node has distance 0 (which is correct since the shortest path from source to itself is 0) and is marked as finalized, while all other nodes have distance infinity (the weakest upper bound), satisfying the invariant.

- **Maintenance: why finalizing the min-dist node is always correct:**
  At each iteration, I finalize the unfinalized node with minimum distance. Because all edge weights are nonnegative, any path to this node through unfinalized nodes would have cost at least the current minimum distance, so the invariant is preserved when this node joins S, and all edges from it are then safely relaxed.

- **Termination: what the invariant guarantees when the algorithm ends:**
  When all nodes have been finalized, the invariant guarantees that every node's distance value is the true shortest-path distance from the source, since every reachable node has been added to S and every unreachable node correctly remains at infinity.

### Part 3c: Why This Matters for the Route Planner

Correct shortest-path distances ensure that I can reliably calculate the true cost of any relic-visit sequence and make optimal routing decisions without wasting torch fuel on sub-optimal paths.

---

## Part 4: Search Design

### Why Greedy Fails

- **The failure mode:** A greedy algorithm that always visits the nearest unvisited relic next makes locally optimal choices that do not guarantee globally optimal total cost, because visiting a far relic first might unlock much cheaper paths to other relics.

- **Counter-example setup:** Using the spec illustration: S has relic neighbors B (cost 1) and C (cost 2); B connects to D (cost 1) and T (cost 1); C connects to T (cost 1); D connects to B (cost 1), C (cost 1), and T (cost 100); all relics B, C, D must be visited.

- **What greedy picks:** Greedy starts at S and greedily picks the nearest relic B (cost 1), then from B picks nearest unvisited D (cost 1), then from D picks nearest unvisited C (cost 1), finally reaches T (cost 1), for a total of 1+1+1+1 = 4.

- **What optimal picks:** The optimal order is S → B (1) → D (1) → C (1) → T (1), also totaling 4, but consider if T from D had cost 50 instead: greedy would waste fuel on that bad path, while reordering to S → C → B → D → T might find T from C is cheaper and save fuel overall.

- **Why greedy loses:** Greedy's inability to look ahead means it cannot see that routing through intermediate relics in a different sequence might connect to cheaper exit paths, missing reorderings that reduce total cost by finding shared cheap intermediate nodes.

### What the Algorithm Must Explore

- I must explore different orders in which to visit relics, because the total fuel cost depends critically on the sequence, and no greedy choice of "which relic next" guarantees that the resulting order is globally optimal.

---

## Part 5: State and Search Space

### Part 5a: State Representation

> Document the three components of your search state as a table.
> Variable names here must match exactly what you use in torchbearer.py.

| Component | Variable name in code | Data type | Description |
|---|---|---|---|
| Current location | | | |
| Relics already collected | | | |
| Fuel cost so far | | | |

### Part 5b: Data Structure for Visited Relics

> Fill in the table.

| Property | Your answer |
|---|---|
| Data structure chosen | |
| Operation: check if relic already collected | Time complexity: |
| Operation: mark a relic as collected | Time complexity: |
| Operation: unmark a relic (backtrack) | Time complexity: |
| Why this structure fits | |

### Part 5c: Worst-Case Search Space

> Two bullets.

- **Worst-case number of orders considered:** _Your answer (in terms of k)._
- **Why:** _One-line justification._

---

## Part 6: Pruning

### Part 6a: Best-So-Far Tracking

> Three bullets.

- **What is tracked:** _Your answer here._
- **When it is used:** _Your answer here._
- **What it allows the algorithm to skip:** _Your answer here._

### Part 6b: Lower Bound Estimation

> Three bullets.

- **What information is available at the current state:** _Your answer here._
- **What the lower bound accounts for:** _Your answer here._
- **Why it never overestimates:** _Your answer here._

### Part 6c: Pruning Correctness

> One to two bullets. Explain why pruning is safe.

- _Your answer here._

---

## References

> Bullet list. If none beyond lecture notes, write that.

- _Your references here._
