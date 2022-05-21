'''
A python dictionary implemented using an AVL tree
https://en.wikipedia.org/wiki/AVL_tree

@author: Alfredo Velasco
'''

from dataclasses import dataclass, field
from pprint import pprint
import itertools
import random
from tqdm import tqdm
from tqdm.auto import trange
from collections import deque
from AVL import AVL, _Node

@dataclass(eq=False, order=False)
class _KeyVal(object):
	key: int = 0
	val: int = 0

	def __lt__(self, other):
		return self.key < other.key

	def __gt__(self, other):
		return self.key > other.key

	def __eq__(self, other):
		return self.key == other.key



@dataclass
class AVL_Dict(AVL):
	"""
	A dictionary that uses an AVL tree
	"""

	def __init__(self, items=None):
		'''
		
		Initializes the tree with the items (if provided)

		:param list( (key, val) pairs) items: list of key-val pairs to insert into the dictionary
		:param dict items: dictionary to copy

		'''
		super(AVL_Dict, self).__init__()

		if items is not None:
			if isinstance(items, dict):
				for key, val in items.items():
					self.add(key, val)
			else:
				for (key, val) in items:
					self.add(key, val)


	def add(self, key, val):
		'''
		Adds a key-val pair to the tree

		:param key: The key to be inserted
		:param val: The value to which key maps
		'''
		if self._n == 0:
			self._root = _Node( _KeyVal(key, val) )
		else:
			self._find_deletion_point( _KeyVal(key, val) )
			curr = self.traversed_node_list[-1]
			# print(f"{self=}")
			# print(f"{key=} {val=} {curr=} {curr.left=} {curr.right=}")
			# print(f"{self.traversed_node_list}")
			# print()
			if curr.item.key == key:
				curr.item = _KeyVal(key, val)
				return
			elif key < curr.item.key and curr.left is None:
				curr.left = _Node(item=_KeyVal(key, val))
			elif curr.item.key < key and curr.right is None:
				curr.right = _Node(item=_KeyVal(key, val) )
			else:
				raise Exception(f"{self=} {item=}\nI didn't think about this situation!")
			self._fix_heights(self.traversed_node_list)
		self._n += 1
		self.traversed_node_list = []


	def remove(self, key):
		'''
		Removes an item from the tree

		:param key: the key to be deleted
		:raises KeyError: if key is not in the tree
		'''
		super().remove(_KeyVal(key, 0))


	def get(self, key):
		'''
		Returns the value to which key maps

		:param key: The key whose mapping we'll retreive
		:return val: The value to which key maps 
		'''
		if self._root is None:
			raise KeyError(f"{key=} is not in the tree!")

		curr = self._root
		while True:
			if curr is None:
				raise KeyError(f"{key=} is not in the tree!")

			if curr.item.key == key:
				return curr.item.val
			elif key < curr.item.key:
				curr = curr.left
			else:
				curr = curr.right


	def __setitem__(self, key, val):
		'''
		Wrappper for the add method
		'''
		self.add(key, val)

	def __getitem__(self, key):
		'''
		Wrappper for the get method
		'''
		return self.get(key)


	def __delitem__(self, key):
		'''
		Wrappper for the remove method
		'''
		self.remove(key)
		# self.remove(_KeyVal(key, 0))

	def __eq__(self, other):
		'''
		Compares the AVL_Dict with other

		:param AVL_Dict other: the AVL_Dict we'll compare
		:param dict other: the dict we'll compare
		'''
		if isinstance(other, AVL_Dict) or isinstance(other, dict):
			if len(other) != len(self):
				return False

			for k, v in self.items_yield():
				if k not in other or other[k] != v:
					return False
			return True

		else:
			return False

	def __contains__(self, key):
		'''
		Tells if you item is in the tree
		param: item - the item to find in the tree
		return: bool - if the item was found in the tree
		'''
		return super().__contains__(_KeyVal(key, 0))


	def keys_yield(self):
		'''
		Generator function that iterates DFS through the keys in the tree

		:returns key: The keys in the tree
		'''
		for key, _ in self.items_yield():
			yield key


	def items_yield(self):
		'''
		Generator function that iterates DFS through the (key, value) pairs in the tree

		:returns (key, val): The key-value pairs in the tree
		'''
		if self._root is None:
			yield from []
		else:
			discovered = set()
			stack = [self._root]

			while stack:
				node = stack[-1]
				if node is None:
					raise Exception("This tree has a None element!")
				if not isinstance(node, _Node):
					raise Exception("This tree has a non-_Node {node} element!")
				
				discovered.add(id(node))

				inserted_left = False
				inserted = False

				if node.left is not None and id(node.left) not in discovered:
					stack.append(node.left)
					inserted_left = True
					inserted = True

				if not inserted_left and node.right is not None and id(node.right) not in discovered:
					stack.append(node.right)
					if not inserted:
						item = stack.pop(-2)
						yield (item.item.key, item.item.val)
					inserted = True

				if not inserted:
					item = stack.pop()
					yield (item.item.key, item.item.val)


	def __next__(self):
		while self.stack:
			node = self.stack[-1]
			if node is None:
				raise Exception("This tree has a None element!")
			if not isinstance(node, _Node):
				raise Exception("This tree has a non-_Node {node} element!")
			
			self.discovered.add(id(node))

			inserted_left = False
			inserted = False

			if node.left is not None and id(node.left) not in self.discovered:
				self.stack.append(node.left)
				inserted_left = True
				inserted = True

			if not inserted_left and node.right is not None and id(node.right) not in self.discovered:
				self.stack.append(node.right)
				if not inserted:
					return self.stack.pop(-2).item.key
				inserted = True

			if not inserted:
				return self.stack.pop().item.key

		raise StopIteration


	def __repr__(self):
		'''
		A string representation of the AVL_Dict

		:returns str result: the string representation of the AVL_Dict
		'''
		if self._root is None:
			return 'AVL_Dict()'
	
		return f"AVL_Dict({self.__dfs_str__(self._root)})"
	
	def __str__(self):
		'''
		A string representation of the AVL_Dict

		:returns str result: the string representation of the AVL_Dict
		'''
		result = '{'
		l = [f"{key}: {self[key]}" for key in self]
		result += ', '.join(l)
		result += '}'
		return result



def main():

	def random_insertion_test():
		# Random insertions of lists
		# We passed!
		t = AVL_Dict()
		for n in trange(100, 101, desc='Insertion size'):
			for x in tqdm(range(10000), desc='Rand loop'):
				t.clear()
				d = dict()
				random.seed(x)
				a = set([(random.randint(0, n), random.randint(0, n)) for x in range(n)])
				for k, v in a:
					t[k] = v
					d[k] = v
					t._verify_itself()
				if d != t:
					raise Exception(f"{x=} results in an error!\n{t}\n{d}")

	def random_duplicate_test():
		# Random duplicates
		# We passed!
		t = AVL_Dict()
		for x in tqdm(range(10000), desc='random duplicates'):
			t.clear()
			random.seed(x)
			l = [random.randint(1, 100) for x in range(1000)]
			s = set(l)
			for i in l:
				t.add(i, i)
				# print(t)
			r = set(t)
			if r != s:
				raise Exception(f"{x=} results in an error!\n{r}\n{s}")


	def contains_test():
		# Check the contains
		# We passed!
		t = AVL_Dict()
		for x in tqdm(range(10000), desc='contains_test'):
			t.clear()
			random.seed(x)
			s = set(random.sample(list(range(1000)), 100))
			c = set(range(1000)) - s

			for i in s:
				t.add(i, i)
			for i in s:
				if i not in t:
					raise Exception(f"{x=} causes an error!")
			for i in c:
				if i in t:
					raise Exception(f"{x=} causes an error!")
	
	def pprint_test():
		# Check the pprint
		t = AVL_Dict()
		for n in range(20):
			t.clear()
			s = {}
			for x in range(n):
				t[x] = x + 1
				s[x] = x + 1
			pprint(t)
			pprint(s)
			print(t)
			print(s)
			print(f"{t=}")
			print(f"{s=}")
			print()
		for x in t:
			print(x)


	def random_mapping_test():
		# Random mappings
		# We passed!
		for n in trange(100, desc='Size loop'):
			for x in trange(1000, desc='Seed loop'):
				random.seed(x)
				s = {random.randint(0, n):random.randint(0, n) for x in range(n)}
				t = AVL_Dict(s)
				for x in s:
					if s[x] != t[x]:
						raise Exception(f"{x=} causes an error!\n{s=}\n{t=}\nx->{s[x]=} != {t[x]=}")

		for x in trange(10000):
			random.seed(x)
			s = {random.randint(0, 1000):random.randint(0, 1000) for x in range(1000)}
			t = AVL_Dict(s)
			for x in s:
				if s[x] != t[x]:
					raise Exception(f"{x=} causes an error!\n{s=}\n{t=}\nx->{s[x]=} != {t[x]=}")

	# Random deletions
	def random_deletion_test():
		for n in trange(100, desc='Random deletion'):
			for x in tqdm(range(1000), desc='Rand loop'):
				random.seed(x)
				a = set([(random.randint(0, n), random.randint(0, n)) for x in range(n)])
				t = AVL_Dict(a)
				d = dict(a)

				for k, v in a:
					if k in d:
						del t[k]
						del d[k]
						t._verify_itself()
					else:
						t[k] = v
						d[k] = v

					if d != t:
						raise Exception(f"{x=} results in an error!\n{t}\n{d}")

	random_insertion_test()
	contains_test()
	random_mapping_test()
	random_deletion_test()
	pprint_test()




if __name__ == '__main__':
	main()
