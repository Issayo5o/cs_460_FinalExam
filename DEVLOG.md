# Development Log – The Torchbearer

**Student Name:** Issa Alwazir
**Student ID:** 131040114

> Instructions: Write at least four dated entries. Required entry types are marked below.
> Two to five sentences per entry is sufficient. Write entries as you go, not all in one
> sitting. Graders check that entries reflect genuine work across multiple sessions.
> Delete all blockquotes before submitting.

---

## Entry 1 – May 14, 2026, 2:00 PM: Initial Plan

Read the full assignment carefully. The problem is combining two phases: (1) precompute shortest paths via Dijkstra from key nodes, and (2) search over relic visitation orders using branch-and-bound pruning. Initial plan: implement Dijkstra first, then precomputation wrapper, then the recursive search with mutable best-so-far tracking. Expect the search to be the trickiest part due to state management and pruning conditions. Will test against the provided test cases after each major phase.

---

## Entry 2 – May 14, 2026, 3:20 PM: Dijkstra Implementation Sprint

I implemented `run_dijkstra()` using a binary heap-based priority queue to handle efficient edge relaxation. I initially had a bug where I was processing nodes from the heap multiple times, causing redundant relaxations; I fixed this by adding a visited set and skipping already-processed nodes. I verified the correctness of my Dijkstra implementation against the provided test cases and confirmed that the distance table structure (nested dict) provides O(1) lookup as required. I also implemented `select_sources()` to identify the spawn, all relics, and the exit node as sources, then used these in `precompute_distances()` to build the complete distance table.

---

## Entry 3 – May 14, 2026, 5:30 PM: Algorithm Correctness Documentation

I filled out Part 3 on the Dijkstra invariant. I wrote the `dijkstra_invariant_check()` function explaining what the invariant means for finalized and non-finalized nodes. I then documented the three phases—initialization, maintenance, and termination—making sure to emphasize how nonnegative edge weights guarantee correctness at each step. I completed README Part 3a, 3b, 3c with detailed explanations connecting the invariant to my search algorithm's correctness. All explanations match between the code function and the README exactly.

---

## Entry 4 – May 14, 2026, 7:00 PM: Search Strategy Documentation

I worked through Part 4 on why greedy fails and what the search must explore. I analyzed the spec illustration (S, B, C, D, T graph) and wrote out the failure mode: greedy picks the nearest unvisited relic but misses that different orders unlock cheaper paths. I provided a concrete counterexample showing how greedy could waste fuel by not seeing ahead. I filled out `explain_search()` and all of README Part 4, explaining why the algorithm must search over different relic visitation orders. The core insight is that no local greedy choice guarantees global optimality when order matters.

---

## Entry 5 – May 14, 2026, 8:30 PM: State and Search Implementation

I implemented `find_optimal_route()` which initializes the search state with an empty set for relics_remaining and a mutable best container tracking the best solution found. I carefully designed the state representation to use current_loc, relics_remaining (as a set for O(1) checks), and cost_so_far. I filled out README Part 5a documenting exact variable names, Part 5b explaining why a set is the right data structure, and Part 5c analyzing the O(k!) worst-case search space. The key insight is that tracking what remains (not what we've collected) makes backtracking natural via recursion unwinding.

---

## Final Entry – May 14, 2026, 10:00 PM: Time Estimate

| Part | Estimated Hours |
|---|---|
| Part 1: Problem Analysis | 0.5 |
| Part 2: Precomputation Design | 1 |
| Part 3: Algorithm Correctness | 0.75 |
| Part 4: Search Design | 0.5 |
| Part 5: State and Search Space | 1.25 |
| Part 6: Pruning | 1.5 |
| Part 7: Implementation | 1 |
| README and DEVLOG writing | 1 |
| **Total** | **7.5** |
