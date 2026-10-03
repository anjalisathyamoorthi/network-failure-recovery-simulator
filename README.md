# 🌐 Network Failure Recovery Simulator

A portfolio-quality Python application that simulates router and link failures in computer networks, identifies disconnected components, alternate shortest routes, and critical single points of failure (bridges and articulation points).

> **Design and Analysis of Algorithms (DAA) Project — Problem 55**  
> Built strictly with **Python 3.10+**, **Streamlit**, **Plotly**, **pandas**, and **pytest**. All core graph algorithms are implemented **by hand from scratch** without external graph library dependencies in the core engine.

---

## 📌 Problem Statement

In mission-critical computer networks, router hardware crashes or fiber-optic link severances can disrupt connectivity and segment networks into isolated components. This application models network topologies as undirected weighted graphs, evaluates network resilience under single or multiple simultaneous failure scenarios, re-computes optimal recovery routes, identifies structural single points of failure (bridges and articulation points via Tarjan's algorithm), and visualizes step-by-step algorithmic execution states.

---

## 🚀 Key Features

1. **Hand-Crafted Core Algorithms**:
   - **Breadth-First Search (BFS)**: Level-by-level traversal using `collections.deque` to compute minimum-hop paths.
   - **Depth-First Search (DFS)**: Iterative stack-based graph traversal recording discovery and finish timestamps.
   - **Dijkstra's Shortest Path**: Least-cost path routing using a Python binary min-heap (`heapq`).
   - **Connected Components**: BFS/DFS graph partitioning with structural equivalence metrics.
   - **Tarjan's Critical Connections**: Single-pass iterative DFS identifying **Bridges** (critical links) and **Articulation Points** (critical routers). Fully recursion-safe for 1000+ node networks.
   - **Failure Recovery Analysis**: Rerouting evaluation, latency increase calculations, and reachability loss metrics.

2. **Interactive Streamlit UI (9 Feature Tabs)**:
   - **🌐 Network**: Interactive Plotly graph showing active vs. failed nodes/links.
   - **🧩 Components**: Color-coded visualization of network partitions and isolated routers.
   - **⚡ Shortest Path (Dijkstra)**: Least-cost routing with distance tables.
   - **🎯 Minimum Hops (BFS)**: Hop-count routing with level tables.
   - **🔄 Alternate Route**: Side-by-side comparison of primary vs. recovery routes and cost increases.
   - **⚠️ Critical Connections**: Highlighting single points of failure on healthy networks.
   - **🔍 Reachability**: Pairwise reachability checks comparing BFS and DFS traversal paths.
   - **🎬 Step-by-Step**: Interactive animation engine with Play/Pause, Next/Prev, Speed control, and detailed state cards.
   - **📊 Comparison & Benchmarks**: Empirical runtime benchmark chart ($V = 50$ to $800$ nodes) and theoretical complexity comparisons.

3. **Topology Presets & Editors**:
   - Campus Enterprise Network, Ring Topology, Star Topology, Core Router Failure Bottleneck, and Random Graph Generator ($V \le 1000$).
   - Custom node/link additions, deletions, and CSV/JSON edge-list import/export.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **User Interface**: Streamlit
- **Graph Visualization**: Plotly Express & Graph Objects (`networkx` used exclusively for 2D layout positioning)
- **Benchmarking & Data**: Pandas, NumPy
- **Unit Testing**: Pytest (with `networkx` cross-verification)

---

## 📦 Installation & Setup

1. **Clone or Download the Repository**:
   ```bash
   cd network-failure-simulator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Unit Tests**:
   ```bash
   pytest tests/ -v
   ```

4. **Launch Application**:
   ```bash
   streamlit run app.py
   ```

---

## 📐 Algorithm Complexity

| Algorithm | Time Complexity | Space Complexity | Data Structure |
| :--- | :--- | :--- | :--- |
| **Breadth-First Search (BFS)** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Queue (`collections.deque`) |
| **Depth-First Search (DFS)** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Explicit Stack |
| **Dijkstra's Algorithm** | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V)$ | Binary Min-Heap (`heapq`) |
| **Connected Components** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Visited Set + Queue/Stack |
| **Tarjan Critical Connections** | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Iterative State Stack + Arrays |

---

## 📸 Network Failure Simulation Flow

### 1. Healthy Campus Network State
```
 [SVR1] -- (1.0) -- [CORE1] ======= (1.0) ======= [CORE2] -- (2.0) -- [SVR2]
                      |                              |
                    (2.0)                          (3.0)
                      |                              |
                   [DIST1] ------ (3.0) ------  [DIST3]
```

### 2. Core Router Failure Rerouting
```
 [SVR1] -- (1.0) -- [CORE1] [X FAILED CORE2 X]
                      |                         
                    (2.0)                       
                      |                         
                   [DIST1] ------ (3.0) ------  [DIST3] ➔ Alternate Route Active
```

---

## 🎯 Design Decisions

1. **Strict Core Independence**: Core algorithm modules (`core/`) do not import or call `networkx` or third-party graph packages. All data structures and logic are implemented from fundamental principles.
2. **Iterative Tarjan Implementation**: Tarjan's algorithm for bridges and articulation points uses an explicit state-machine stack instead of recursion to prevent `RecursionError` call-stack crashes on large random graphs ($V \ge 1000$).
3. **Non-Destructive Failure Simulation**: Failures are managed via `failed_nodes` and `failed_edges` sets, allowing real-time toggling and undo operations without modifying underlying network geometry.

---

## 🔮 Limitations & Future Work

- **Directed Edges**: Currently supports undirected links; future versions will support asymmetric directed routing policies (BGP/OSPF).
- **Link Capacity & Flow**: Incorporating bandwidth constraints via Max-Flow / Min-Cut algorithms (Edmonds-Karp).
- **Automated Resilience Optimization**: Recommending optimal new backup links to eliminate single points of failure.
- **Dynamic Multi-Failure Cascades**: Simulating cascading router overloads when traffic shifts to backup links.
