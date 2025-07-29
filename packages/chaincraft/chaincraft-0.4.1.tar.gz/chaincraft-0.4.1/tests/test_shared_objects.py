# tests/test_shared_objects.py

from typing import List
import unittest
import random
import time
import os
import sys
import json
import hashlib

# Try to import from installed package first, fall back to direct imports
try:
    from chaincraft.shared_object import SharedObject
    from chaincraft.shared_message import SharedMessage
    from chaincraft import ChaincraftNode
except ImportError:
    # Add parent directory to path as fallback
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from chaincraft.shared_object import SharedObject
    from chaincraft.shared_message import SharedMessage
    from chaincraft import ChaincraftNode

random.seed(7331)


class SimpleSharedNumber(SharedObject):
    def __init__(self):
        self.number = 0
        self.messages = []
        self.seen_hashes = set()

    def is_valid(self, message: SharedMessage) -> bool:
        # We only accept integer data in this example
        return isinstance(message.data, int)

    def add_message(self, message: SharedMessage) -> None:
        """
        Deduplicate by hashing the message's 'data' field (ignoring the signature).
        That way, if the same data is gossiped multiple times with different signatures,
        we still only increment once.
        """
        # Convert the integer data -> a consistent string
        data_str = json.dumps({"content": message.data}, sort_keys=True)
        msg_hash = hashlib.sha256(data_str.encode()).hexdigest()

        if msg_hash in self.seen_hashes:
            # Already incremented for this data
            return

        self.seen_hashes.add(msg_hash)

        # Now increment
        self.number += message.data
        self.messages.append(message)
        print(f"SimpleSharedNumber: Added message with data: {message.data}")

    def is_merkelized(self) -> bool:
        return False

    def get_latest_digest(self) -> str:
        return str(self.number)

    def has_digest(self, hash_digest: str) -> bool:
        return hash_digest in self.digests

    def is_valid_digest(self, hash_digest: str) -> bool:
        return True

    def add_digest(self, hash_digest: str) -> bool:
        self.digests.append(hash_digest)
        return True

    def gossip_object(self, peer, digest) -> List[str]:
        return []

    def get_messages_since_digest(self, digest: str) -> List[SharedMessage]:
        return []


def create_network(num_nodes, reset_db=False):
    nodes = [ChaincraftNode(reset_db=reset_db, debug=False) for _ in range(num_nodes)]
    for node in nodes:
        node.add_shared_object(SimpleSharedNumber())
        node.start()
    return nodes


def connect_nodes(nodes):
    # Connect each node to its immediate neighbors in a ring
    num_nodes = len(nodes)
    for i in range(num_nodes):
        # Connect to next node (wrapping around to 0 at the end)
        next_node = (i + 1) % num_nodes
        nodes[i].connect_to_peer(nodes[next_node].host, nodes[next_node].port)
        nodes[next_node].connect_to_peer(nodes[i].host, nodes[i].port)

        # Optional: Connect to previous node as well if you want bidirectional connections
        # prev_node = (i - 1) % num_nodes
        # nodes[i].connect_to_peer(nodes[prev_node].host, nodes[prev_node].port)
        # nodes[prev_node].connect_to_peer(nodes[i].host, nodes[i].port)


def wait_for_propagation(nodes, shared_object_index, expected_number, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        numbers = [node.shared_objects[shared_object_index].number for node in nodes]
        print(f"Current shared numbers: {numbers}")
        if all(number == expected_number for number in numbers):
            return True
        time.sleep(1.0)
    return False


class TestChaincraftNetwork(unittest.TestCase):
    def setUp(self):
        self.num_nodes = 5
        self.nodes = create_network(self.num_nodes, reset_db=True)
        connect_nodes(self.nodes)
        time.sleep(2)  # Wait for initial connections to establish

    def tearDown(self):
        for node in self.nodes:
            node.close()

    def test_network_creation(self):
        self.assertEqual(len(self.nodes), self.num_nodes)
        for node in self.nodes:
            self.assertTrue(node.is_running)
            self.assertTrue(0 < len(node.peers) <= node.max_peers)

    def test_shared_object_propagation(self):
        for i in range(self.num_nodes):
            self.nodes[i].create_shared_message(i + 1)
            time.sleep(1)  # Wait a bit between message creations
            for node in self.nodes:
                print(
                    f"Node {node.port}: Shared number: {node.shared_objects[0].number}"
                )

        expected_number = sum(range(1, self.num_nodes + 1))
        self.assertTrue(
            wait_for_propagation(self.nodes, 0, expected_number, timeout=20)
        )


if __name__ == "__main__":
    unittest.main()
