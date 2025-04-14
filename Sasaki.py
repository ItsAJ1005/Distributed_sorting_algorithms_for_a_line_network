"""
Implementation of Sasaki's Time-Optimal Sorting Algorithm by AJ Harsh Vardhan using sockets

Based on:
Sasaki, E. (1991). Time-optimal distributed sorting algorithm. 
Information Processing Letters, 40(3), 153-157.
Cited paper: Sasaki, Atsushi. (2002). A time-optimal distributed sorting algorithm on a line network. Information Processing Letters. 83. 21-26. 10.1016/S0020-0190(01)00307-6. 

This is an educational implementation for an Assignment given by 
Dr Rajendra Prasath in the year 2025 @IIITS.
"""

import time
import random
import argparse
from datetime import datetime
 
"""
- Time Complexity: Approximately O(n²) depending on message passing overhead and number of local comparisons.
- Space Complexity: O(n) for node objects and the auxiliary message queue.
- Data Structures: Custom classes (Node, Element), along with a list used as the message queue.
"""

class Element:
    def __init__(self, value, is_marked=False):
        self.value = value
        self.is_marked = is_marked

class Node:
    def __init__(self, node_id, total_nodes, values=None):
        self.id = node_id
        self.total_nodes = total_nodes
        
        # Initialize elements based on position
        if node_id == 0:
            self.lValue = Element(-float('inf'), False)
            self.rValue = Element(values[0], True) if values else Element(random.randint(1, 2000), True)
        elif node_id == total_nodes - 1:
            self.lValue = Element(values[-1], True) if values else Element(random.randint(1, 2000), True)
            self.rValue = Element(float('inf'), False)
        else:
            val = values[node_id] if values else random.randint(1, 2000)
            self.lValue = Element(val, False)
            self.rValue = Element(val, False)
        
        self.area = -1 if node_id == 0 else 0
        self.left = node_id - 1 if node_id > 0 else None
        self.right = node_id + 1 if node_id < total_nodes - 1 else None
        
        # Statistics
        self.comparisons = 0
        self.swaps = 0
        self.messages_sent = 0

    def process_message(self, message, message_queue):
        if message.msg_type == "COMPARE":
            self.handle_comparison(message_queue)
        elif message.msg_type == "SYNC":
            self.send_message(message_queue, message.sender, "ACK")

    def handle_comparison(self, message_queue):
    # Compare with left neighbor
        if self.left is not None:
            self.comparisons += 1 
            left_node = message_queue.nodes[self.left]
            if left_node.rValue.value > self.lValue.value:
                self.swap_elements(left_node.rValue, self.lValue, message_queue)
                self.adjust_area(left_node, self, message_queue)

        # Compare with right neighbor
        if self.right is not None:
            self.comparisons += 1 
            right_node = message_queue.nodes[self.right]
            if right_node.lValue.value < self.rValue.value:
                self.swap_elements(self.rValue, right_node.lValue, message_queue)
                self.adjust_area(self, right_node, message_queue)

        # Internal comparison
        self.comparisons += 1
        if self.lValue.value > self.rValue.value:
            self.lValue, self.rValue = self.rValue, self.lValue
            self.swaps += 1


    def swap_elements(self, elem1, elem2, message_queue):
        elem1.value, elem2.value = elem2.value, elem1.value
        elem1.is_marked, elem2.is_marked = elem2.is_marked, elem1.is_marked
        self.swaps += 1
        self.send_message(message_queue, self.id, "SWAP")

    def adjust_area(self, source, target, message_queue):
        if source.rValue.is_marked:
            target.area -= 1
        if target.lValue.is_marked:
            target.area += 1
        self.send_message(message_queue, target.id, "ADJUST_AREA")

    def send_message(self, message_queue, receiver, msg_type):
        message_queue.append(Message(self.id, receiver, msg_type))
        self.messages_sent += 1

class MessageQueue:
    def __init__(self, nodes):
        self.queue = []
        self.nodes = nodes

    def append(self, message):
        self.queue.append(message)

    def process_all(self):
        while self.queue:
            msg = self.queue.pop(0)
            if msg.receiver is not None:
                self.nodes[msg.receiver].process_message(msg, self)

class Message:
    def __init__(self, sender, receiver, msg_type):
        self.sender = sender
        self.receiver = receiver
        self.msg_type = msg_type
        self.timestamp = time.time()

def simulate_sasaki_sort(n, initial_values=None):
    nodes = [Node(i, n, initial_values) for i in range(n)]
    mq = MessageQueue(nodes)

    start_time = time.time()

    # Run n-1 phases as per Sasaki's algorithm
    for phase in range(n-1):
        # Trigger comparisons in all nodes
        for node in nodes:
            mq.append(Message(None, node.id, "COMPARE"))
        mq.process_all()

        # Synchronization phase
        for node in nodes:
            if node.right is not None:
                mq.append(Message(node.id, node.right, "SYNC"))
        mq.process_all()

    # Collect results
    sorted_values = []
    current = nodes[0]
    while current:
        if current.area == -1:
            sorted_values.append(current.rValue.value)
        else:
            sorted_values.append(current.lValue.value)
        current = nodes[current.right] if current.right is not None else None

    # Verify sorting
    is_sorted = all(sorted_values[i] <= sorted_values[i+1] for i in range(len(sorted_values)-1))

    return {
        'time': time.time() - start_time,
        'comparisons': sum(n.comparisons for n in nodes),
        'swaps': sum(n.swaps for n in nodes),
        'messages': sum(n.messages_sent for n in nodes),
        'sorted': sorted_values,
        'is_sorted': is_sorted
    }

def main():
    parser = argparse.ArgumentParser(description='Simulate Sasaki\'s Time-Optimal Sort')
    parser.add_argument('--nodes', type=int, default=10, help='Number of nodes')
    parser.add_argument('--seed', type=int, default=None, help='Random seed')
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    print(f"Running Sasaki's algorithm with {args.nodes} nodes...")
    results = simulate_sasaki_sort(args.nodes)

    print("\nSorted values:")
    print(results['sorted'])
    print(f"\nTime: {results['time']:.4f}s")
    print(f"Comparisons: {results['comparisons']}")
    print(f"Exchanges/Swaps: {results['swaps']}")
    print(f"Messages: {results['messages']}")
    print(f"Correctly sorted: {results['is_sorted']}")

if __name__ == "__main__":
    main()