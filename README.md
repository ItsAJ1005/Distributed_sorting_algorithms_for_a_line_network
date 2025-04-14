# Distributed Sorting Algorithms

This project implements three distributed sorting algorithms on a line network using basic primitive operations (send, receive, and compute) in a discrete event simulator.

## Implemented Algorithms

1. **Odd-Even Transposition Sort**
2. **Sasaki's Time-Optimal Sort**
3. **Alternative Time-Optimal Sort**

Each algorithm is implemented in its own program file, and all programs simulate communication between processing entities (nodes) arranged in a line network.

## Files

- `odd_even_sort.py` - Implements Odd-Even Transposition Sort
- `Sasaki.py` - Implements Sasaki's Time-Optimal Algorithm
- `Alternative.py` - Implements the Alternative Time-Optimal Algorithm (supports both sequential and multi-threaded approaches)
- `README.md` - This documentation file
- Output Screenshots - The screenshots of results
- `Comparison_table.png` - Comparisons of algorithms

## Requirements

- Python 3.x

## Usage Instructions

### Odd-Even Transposition Sort

```bash
python odd_even_sort.py --nodes <n> [--seed <seed_value>] [--input-mode random/manual]
```

Example:
```bash
python odd_even_sort.py --nodes=10 --seed=42 --input-mode=random
```
- `random` for self array initialization and `manual` for entering array elements
- `seed` to get same result in random for all algorithms

### Sasaki's Time-Optimal Sort

```bash
python Sasaki.py --nodes <n> [--seed <seed_value>]
```

Example:
```bash
python Sasaki.py --nodes 20 --seed 10
```

### Alternative Time-Optimal Sort

```bash
python Alternative.py --nodes <n> [--seed <seed_value>] [--input-mode random/manual] [--method sequential/threaded]
```

Example:
```bash
python Alternative.py --nodes 30 --seed 100 --input-mode random --method threaded
```

## Output

Each program prints the following information after execution:
- The initial unsorted array (or values) used
- The final sorted array
- Detailed statistics including:
  - Total execution time
  - Number of comparisons
  - Swaps/exchanges performed
  - Messages sent (where applicable)
  - A flag indicating if the array is correctly sorted

For the Alternative Time-Optimal Sort, results are additionally saved in a timestamped output file for logging.

## Running Experiments

For comprehensive analysis, execute each algorithm with these numbers of processing entities: n = 10, 20, 30, and 50.

Record the following metrics for a comparison table:
- Execution Time
- Total Comparisons
- Total Exchanges/Swaps
- Messages Sent (if applicable)

## Algorithm Descriptions

### Odd-Even Transposition Sort

This algorithm divides the sorting process into phases where nodes compare and possibly swap values with their neighbors:
- In even-numbered phases, even-indexed nodes send their values to the right, while odd-indexed nodes receive these values
- In odd-numbered phases, the roles are reversed
- The process repeats for n phases, ensuring that adjacent pairs are compared and the array gradually becomes sorted
- Communication between nodes is simulated with message passing in a discrete-event queue

### Sasaki's Time-Optimal Sort

Sasaki's algorithm uses a message-passing mechanism between distributed nodes arranged in a line:
- Each node holds elements (with some marked as boundaries using positive or negative infinity to aid comparisons at the extremities)
- Nodes exchange messages to compare their own values with their neighbors' appropriate elements
- When an out-of-order pair is detected, a swap occurs, and auxiliary "area" adjustments are made to track the local state
- This approach optimizes time by operating concurrently over the network, though it tends to use more communication messages

### Alternative Time-Optimal Sort

#### Overview
The Alternative Time-Optimal Sort is designed to perform distributed sorting by focusing on a "center-based" comparison within consecutive triplets of elements. The algorithm processes the array over n−1 rounds. In each round, a "center" index is selected based on a cyclic pattern (using modulo arithmetic) to ensure every index is eventually used as the pivot.

#### Operation
1. For each selected center (which is spaced by 3 units to avoid overlapping comparisons), the algorithm examines the element at the center and its immediate left and right neighbors
2. For non-edge cases, the three values are rearranged in sorted order:
   - Compute the minimum, maximum, and the middle value by simple pairwise comparisons
   - Only count an exchange if the value changes
3. For edge cases (when the center is the first or last element), comparisons are made only with the available neighbor

#### Multi-threaded Version
- In the threaded implementation, each center-based triplet sorting task is run concurrently on its own thread
- Python's threading module is used with proper synchronization (using Locks) to update shared statistics (comparisons, exchanges) without race conditions
- Threads for a given round are all started concurrently and then joined to ensure all tasks complete before the next round starts

#### Data Structures and Complexity
- The array is represented by a list of integers. Additional data structures include dictionaries for shared statistics in the multi-threaded approach and lists for thread management
- **Time Complexity**: The algorithm performs approximately O(n) rounds with local operations on constant-sized triplets. While each round is O(n/3) in comparisons, overall complexity is influenced by constant factors; the multi-threaded approach can improve wall-clock time if threads run truly concurrently
- **Space Complexity**: O(n) is required for the array plus additional overhead for threads and locks

#### Key Advantages
- The center-based approach minimizes interference between concurrent operations as non-overlapping segments are processed in parallel
- The design's simplicity allows for efficient implementations both in sequential and parallel forms

#### Communication
Unlike the other two algorithms which simulate explicit message passing, the Alternative Time-Optimal Sort focuses on computation and local data swaps. Thus, it doesn't involve explicit messages except for the synchronization inherent in the multi-threaded method.

## Algorithm Analysis

### Odd-Even Transposition Sort
- **Time Complexity**: O(n²) worst-case due to n phases with O(n) comparisons each
- **Space Complexity**: O(n) for storing node values and communication message queues
- **Data Structures**: Lists for nodes and for simulating message queues

### Sasaki's Time-Optimal Sort
- **Time Complexity**: Approximately O(n²) depending on message passing overhead and number of local comparisons
- **Space Complexity**: O(n) for node objects and the auxiliary message queue
- **Data Structures**: Custom classes (Node, Element), along with a list used as the message queue

### Alternative Time-Optimal Sort
- **Time Complexity**: O(n) rounds over O(n/3) comparisons per round; overhead depends on constant factors
- **Space Complexity**: O(n) for the array plus additional multi-threading overhead in the concurrent version
- **Data Structures**: Lists for the main array, thread collections, and dictionaries with Lock objects for sharing statistics
- The multi-threaded variant leverages parallelism to potentially reduce effective runtime on multi-core systems

## Additional Notes

- All programs mimic a distributed system using simulated communication (message queues for the first two algorithms)
- Each source file is commented extensively to clarify design decisions and implementation details
- Output files are generated by the Alternative Time-Optimal Sort for later analysis