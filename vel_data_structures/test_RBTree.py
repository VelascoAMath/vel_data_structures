import collections
import random
from unittest import TestCase

import tqdm

from RBTree import RBTree


class TestRBTree(TestCase):
    tree_size = 3
    
    def test_delete(self):
        for seed in tqdm.tqdm(range(1000)):
            random.seed(seed)
            l = list(range(TestRBTree.tree_size))
            random.shuffle(l)
            t = RBTree(l)
            while l:
                item = l.pop()
                print(item, t)
                t.remove(item)
                print(t)
                
                self.assertEqual(set(l), set(t))
    
    def test_insert(self):
        for seed in tqdm.tqdm(range(1000)):
            random.seed(seed)
            t = RBTree()
            l = list(range(TestRBTree.tree_size))
            random.shuffle(l)
            
            for index, i in enumerate(l):
                t.insert(i)
                self.assertTrue(t.verify())
                self.assertEqual(set(l[: (index + 1)]), set(t))
            
            l.sort()
            if list(t) != l:
                raise Exception(f"NO {seed=}")
    
    def test_duplicate_insert(self):
        for seed in tqdm.tqdm(range(1000)):
            random.seed(seed)
            t = RBTree()
            l = [random.randint(0, 100) for _ in range(TestRBTree.tree_size)]
            random.shuffle(l)
            
            for index, i in enumerate(l):
                t.insert(i)
                self.assertTrue(t.verify())
                self.assertEqual(
                    collections.Counter(l[: (index + 1)]), collections.Counter(t)
                )
            
            l.sort()
            if list(t) != l:
                raise Exception(f"NO {seed=}")
    
    def test_contains(self):
        for seed in tqdm.tqdm(range(1000)):
            random.seed(seed)
            t = RBTree()
            l = list(range(TestRBTree.tree_size))
            random.shuffle(l)
            for i in l:
                self.assertFalse(i in t)
            
            test_set = set()
            for i in enumerate(l):
                t.insert(i)
                test_set.add(i)
                self.assertSetEqual(set(t), test_set)
                for j in enumerate(l):
                    self.assertEqual(j in test_set, j in t)
