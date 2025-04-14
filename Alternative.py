import time
import argparse
import random
from multiprocessing import Process, Manager, Value, Array
from datetime import datetime

"""
- Time Complexity: O(n) rounds over O(n/3) comparisons per round; overhead depends on constant factors.
- Space Complexity: O(n) for the array plus additional multi-threading overhead in the concurrent version.
- Data Structures: Lists for the main array, thread collections, and dictionaries with Lock objects for sharing statistics.
- The multi-threaded variant leverages parallelism to potentially reduce effective runtime on multi-core systems.
"""

def print_array(arr):
    print(' '.join(map(str, arr)))

def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]
    return 1  

def minimum(a, b):
    return a if a < b else b

def maximum(a, b):
    return a if a > b else b

def is_sorted(arr):
    return all(arr[i] <= arr[i+1] for i in range(len(arr)-1))

# Multi thread immplementation unlike the remaining two algorithms with sockets
def simulate_alternate_time_optimal_sort(n, input_array=None):
    # Initialize stats
    comparisons = 0
    exchanges = 0
    
    if input_array:
        arr = input_array.copy()
    else:
        arr = [random.randint(1, 1000) for _ in range(n)]
    
    initial_values = arr.copy()
    
    # Time the sorting process
    start_time = time.time()
    
    # For n - 1 rounds
    for i in range(1, n):
        remainder = (i + 1) % 3
        if remainder == 0:
            j = 2
        elif remainder == 1:
            j = 0
        else:
            j = 1
        
        # For all centers possible at a distance of 3
        while j < n:
            comparisons += 1
            center = j
            
            # Edge case
            if center - 1 < 0:
                if arr[center] > arr[center + 1]:
                    exchanges += swap(arr, center, center + 1)
            elif center + 1 >= n:
                if arr[center] < arr[center - 1]:
                    exchanges += swap(arr, center, center - 1)
            # Non-edge case
            else:
                min_value = minimum(arr[center], minimum(arr[center - 1], arr[center + 1]))
                max_value = maximum(arr[center], maximum(arr[center - 1], arr[center + 1]))
                mid_value = arr[center] + arr[center - 1] + arr[center + 1] - min_value - max_value
                
                # Only count as exchanges if values actually change
                if arr[center - 1] != min_value:
                    exchanges += 1
                if arr[center] != mid_value:
                    exchanges += 1
                if arr[center + 1] != max_value:
                    exchanges += 1
                    
                arr[center - 1] = min_value
                arr[center + 1] = max_value
                arr[center] = mid_value
            
            j += 3
    
    end_time = time.time()
    
    # Prepare results
    results = {
        'algorithm': 'Alternate Time Optimal Sort',
        'nodes': n,
        'time': end_time - start_time,
        'comparisons': comparisons,
        'exchanges': exchanges,
        'messages': 0,  # No messages since we're not using sockets
        'initial_values': initial_values,
        'final_values': arr,
        'is_sorted': is_sorted(arr)
    }
    
    return results

# Multi-threaded version without sockets (more reliable)
def multi_threaded_sort(arr, n, stats_dict):
    from threading import Thread, Lock
    
    # Create a lock for updating shared statistics
    stats_lock = Lock()
    
    # Function for thread to perform comparison operation
    def compare_operation(center):
        comparisons = 0
        exchanges = 0
        
        # Edge case
        if center - 1 < 0:
            comparisons += 1
            if arr[center] > arr[center + 1]:
                exchanges += swap(arr, center, center + 1)
        elif center + 1 >= n:
            comparisons += 1
            if arr[center] < arr[center - 1]:
                exchanges += swap(arr, center, center - 1)
        # Non-edge case
        else:
            comparisons += 1
            min_value = minimum(arr[center], minimum(arr[center - 1], arr[center + 1]))
            max_value = maximum(arr[center], maximum(arr[center - 1], arr[center + 1]))
            mid_value = arr[center] + arr[center - 1] + arr[center + 1] - min_value - max_value
            
            # Only count as exchanges if values actually change
            if arr[center - 1] != min_value:
                exchanges += 1
            if arr[center] != mid_value:
                exchanges += 1
            if arr[center + 1] != max_value:
                exchanges += 1
                
            arr[center - 1] = min_value
            arr[center + 1] = max_value
            arr[center] = mid_value
        
        # Update shared statistics
        with stats_lock:
            stats_dict['comparisons'] += comparisons
            stats_dict['exchanges'] += exchanges
    
    # For n - 1 rounds
    for i in range(1, n):
        remainder = (i + 1) % 3
        if remainder == 0:
            j = 2
        elif remainder == 1:
            j = 0
        else:
            j = 1
        
        threads = []
        
        # For all centers possible at a distance of 3
        while j < n:
            thread = Thread(target=compare_operation, args=(j,))
            threads.append(thread)
            thread.start()
            j += 3
        
        # Wait for all threads to complete before starting next round
        for thread in threads:
            thread.join()
    
    return arr

# Function to simulate the sorting algorithm with multi-threading and return results
def simulate_alternate_time_optimal_sort_threaded(n, input_array=None):
    # Initialize stats
    stats = {
        'comparisons': 0,
        'exchanges': 0
    }
    
    # Create initial array
    if input_array:
        arr = input_array.copy()
    else:
        arr = [random.randint(1, 1000) for _ in range(n)]
    
    initial_values = arr.copy()
    
    # Time the sorting process
    start_time = time.time()
    sorted_arr = multi_threaded_sort(arr, n, stats)
    end_time = time.time()
    
    # Prepare results
    results = {
        'algorithm': 'Alternate Time Optimal Sort (Multi-threaded)',
        'nodes': n,
        'time': end_time - start_time,
        'comparisons': stats['comparisons'],
        'exchanges': stats['exchanges'],
        'messages': 0,  # No messages since we're not using sockets
        'initial_values': initial_values,
        'final_values': sorted_arr,
        'is_sorted': is_sorted(sorted_arr)
    }
    
    return results

# Driver function of the program
def main():
    parser = argparse.ArgumentParser(description='Alternate Time Optimal Sorting')
    parser.add_argument('--nodes', type=int, default=10, help='Number of elements in the sequence')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--input-mode', choices=['random', 'manual'], default='random', 
                        help='Choose between random numbers or manual input')
    parser.add_argument('--method', choices=['sequential', 'threaded'], default='threaded',
                        help='Choose implementation method')
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    input_array = None
    if args.input_mode == 'manual':
        print("Enter your sequence (space-separated integers):")
        input_array = list(map(int, input().split()))
        args.nodes = len(input_array)  # Override nodes with the actual input length
    
    # Run simulation
    print(f"Running Alternate Time Optimal Sorting with {args.nodes} nodes...")
    
    if args.method == 'sequential':
        results = simulate_alternate_time_optimal_sort(args.nodes, input_array)
    else:  # threaded
        results = simulate_alternate_time_optimal_sort_threaded(args.nodes, input_array)
    
    # Print results
    print("\nInitial state:")
    print(results['initial_values'])
    
    print("\nFinal state:")
    print(results['final_values'])
    
    print(f"\nSorting completed in {results['time']:.4f} seconds")
    print(f"Total comparisons: {results['comparisons']}")
    print(f"Total exchanges: {results['exchanges']}")
    if 'messages' in results:
        print(f"Total messages sent: {results['messages']}")
    print(f"Correctly sorted: {results['is_sorted']}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"alternate_time_optimal_sort_results_{args.nodes}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"Algorithm: {results['algorithm']}\n")
        f.write(f"Number of nodes: {results['nodes']}\n")
        f.write(f"Total time: {results['time']:.4f} seconds\n")
        f.write(f"Total comparisons: {results['comparisons']}\n")
        f.write(f"Total exchanges: {results['exchanges']}\n")
        if 'messages' in results:
            f.write(f"Total messages sent: {results['messages']}\n")
        f.write(f"Correctly sorted: {results['is_sorted']}\n")
        f.write("\nInitial values:\n")
        f.write(str(results['initial_values']) + "\n")
        f.write("\nFinal values:\n")
        f.write(str(results['final_values']) + "\n")
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    main()