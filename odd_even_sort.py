import time
import random
import argparse
from datetime import datetime

# msg types = "VALUE", "SWAP", "KEEP", "SYNC", "ACK"

"""
   - Time Complexity: O(n²) worst-case due to n phases with O(n) comparisons each.
   - Space Complexity: O(n) for storing node values and communication message queues.
   - Data Structures: Lists for nodes and for simulating message queues.
"""

class Node:
    def __init__(self, nodeID, totalNodes, value=None):
        self.id = nodeID
        self.totalNodes = totalNodes
        self.value = value if value is not None else random.randint(1, 2000)
        self.left_neighbor = self.id - 1 if self.id > 0 else None
        self.right_neighbor = self.id + 1 if self.id < totalNodes - 1 else None
        
        self.comparisons = 0
        self.exchanges = 0
        self.messages_sent = 0
        
    def process_message(self, msg, messageQueue):
        if msg.msg_type == "VALUE":
            if msg.sender == self.left_neighbor:
                self.compareWithLeft(msg.value, messageQueue)
            elif msg.sender == self.right_neighbor:
                self.compareWithRight(msg.value, messageQueue)
        
        elif msg.msg_type == "SWAP":
            # Exchange the values in nodes
            old_value = self.value
            self.value = msg.value
            self.exchanges += 1
            
        elif msg.msg_type == "KEEP":
            # Same, no changes
            pass
            
        elif msg.msg_type == "SYNC":
            # Acknowledge synchronization
            self.sendMessage(messageQueue, msg.sender, "ACK")
            
        elif msg.msg_type == "START_PHASE":
            # logic for distributed sorting with odd even transposition
            phase = msg.value
            if phase % 2 == 0:  # Even phase
                if self.id % 2 == 0 and self.right_neighbor is not None:
                    self.sendMessage(messageQueue, self.right_neighbor, "VALUE", self.value)
                elif self.id % 2 == 1 and self.left_neighbor is not None:
                    self.sendMessage(messageQueue, self.left_neighbor, "VALUE", self.value)
            else:  # Odd phase
                if self.id % 2 == 0 and self.left_neighbor is not None:
                    self.sendMessage(messageQueue, self.left_neighbor, "VALUE", self.value)
                elif self.id % 2 == 1 and self.right_neighbor is not None:
                    self.sendMessage(messageQueue, self.right_neighbor, "VALUE", self.value)
    
    def compareWithRight(self, neighbourValue, messageQueue):
        self.comparisons += 1
        if self.value > neighbourValue:
            # Need to swap
            old_value = self.value
            self.value = neighbourValue
            self.sendMessage(messageQueue, self.right_neighbor, "SWAP", old_value)
            self.exchanges += 1
        else:
            # Keep current values
            self.sendMessage(messageQueue, self.right_neighbor, "KEEP")
    
    def compareWithLeft(self, neighbourValue, messageQueue):
        self.comparisons += 1
        if self.value < neighbourValue:
            # Need to swap
            old_value = self.value
            self.value = neighbourValue
            self.sendMessage(messageQueue, self.left_neighbor, "SWAP", old_value)
            self.exchanges += 1
        else:
            # Keep current values
            self.sendMessage(messageQueue, self.left_neighbor, "KEEP")
    
    def sendMessage(self, messageQueue, receiver, msg_type, value=None):
        messageQueue.append(Message(self.id, receiver, msg_type, value))
        self.messages_sent += 1
    
    def get_stats(self):
        return {
            'nodeID': self.id,
            'value': self.value,
            'comparisons': self.comparisons,
            'exchanges': self.exchanges,
            'messages_sent': self.messages_sent
        }

def simulate_odd_even_sort(n, initial_values=None):
    # Initialize nodes
    nodes = []
    for i in range(n):
        value = initial_values[i] if initial_values and i < len(initial_values) else None
        nodes.append(Node(i, n, value))
    
    messageQueue = []
    
    start_time = time.time()
    
    # Record initial state
    initial_state = [node.value for node in nodes]
    
    for phase in range(n):
        # Start phase one by one
        for node in nodes:
            # Send phase start msg to each node
            msg = Message(None, node.id, "START_PHASE", phase)
            messageQueue.append(msg)
        
        # Process all messages for this phase
        while messageQueue:
            msg = messageQueue.pop(0)
            if msg.receiver is not None:
                nodes[msg.receiver].process_message(msg, messageQueue)
        
        # Synchronize after each phase
        for i in range(n):
            if i < n - 1:
                nodes[i].sendMessage(messageQueue, i + 1, "SYNC")
        
        # Process all sync messages
        while messageQueue:
            msg = messageQueue.pop(0)
            if msg.receiver is not None:
                nodes[msg.receiver].process_message(msg, messageQueue)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Get final state and statistics
    final_state = [node.value for node in nodes]
    
    total_comparisons = sum(node.comparisons for node in nodes)
    total_exchanges = sum(node.exchanges for node in nodes)
    total_messages = sum(node.messages_sent for node in nodes)
    
    # Verify sorting
    is_sorted = all(final_state[i] <= final_state[i+1] for i in range(len(final_state)-1))
    
    return {
        'algorithm': 'Odd-Even Transposition Sort',
        'nodes': n,
        'time': elapsed_time,
        'comparisons': total_comparisons,
        'exchanges': total_exchanges,
        'messages': total_messages,
        'initial_values': initial_state,
        'final_values': final_state,
        'is_sorted': is_sorted
    }
    
class Message:
    def __init__(self, sender, receiver, msg_type, value=None):
        self.sender = sender
        self.receiver = receiver
        # msg types = "VALUE", "SWAP", "KEEP", "SYNC", "ACK"
        self.msg_type = msg_type
        self.value = value
        self.timestamp = time.time()

def main():
    parser = argparse.ArgumentParser(description='Odd-Even Transposition Sort')
    parser.add_argument('--nodes', type=int, default=10, help='Number of nodes given by user in args')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--input-mode', choices=['random', 'manual'], default='random',
                        help='Choose between random numbers or manual input')
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    # Handle input mode
    initial_values = None
    if args.input_mode == 'manual':
        print("Enter your sequence (space-separated integers):")
        initial_values = list(map(int, input().split()))
        args.nodes = len(initial_values)  # Override nodes with the actual input length
    
    # Run simulation
    print(f"Running Odd-Even Transposition Sort with {args.nodes} nodes...")
    results = simulate_odd_even_sort(args.nodes, initial_values)
    
    # Print results
    print("\nInitial state:")
    print(results['initial_values'])
    
    print("\nFinal state:")
    print(results['final_values'])
    
    print(f"\nSorting completed in {results['time']:.4f} seconds")
    print(f"Total comparisons: {results['comparisons']}")
    print(f"Total exchanges: {results['exchanges']}")
    print(f"Total messages sent: {results['messages']}")
    print(f"Correctly sorted: {results['is_sorted']}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"odd_even_sort_results_{args.nodes}_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"Algorithm: {results['algorithm']}\n")
        f.write(f"Number of nodes: {results['nodes']}\n")
        f.write(f"Total time: {results['time']:.4f} seconds\n")
        f.write(f"Total comparisons: {results['comparisons']}\n")
        f.write(f"Total exchanges: {results['exchanges']}\n")
        f.write(f"Total messages sent: {results['messages']}\n")
        f.write(f"Correctly sorted: {results['is_sorted']}\n")
        f.write("\nInitial values:\n")
        f.write(str(results['initial_values']) + "\n")
        f.write("\nFinal values:\n")
        f.write(str(results['final_values']) + "\n")
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    main()