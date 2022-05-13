'''
@author: Alfredo Velasco
'''

from dataclasses import dataclass, field
from pprint import pprint
import itertools
import random
from tqdm import tqdm
from tqdm.auto import trange
from collections import deque

@dataclass
class _Node(object):
	"""docstring for _Node"""

	key:     int = None
	val:     int = None
	height:  int = 1
	balance: int = 0
	left:    int = None
	right:   int = None

	def __repr__(self):
		return f"{self.key}:{self.val} {self.height=} {self.balance=}"


# @dataclass
class AVL_Dict(object):
	"""Represents an AVL_Dict tree"""

	n: int = 0
	root: _Node = None

	def __init__(self, items=None):
		self.__post_init__()

		if items is not None:
			if isinstance(items, dict):
				for key, val in items.items():
					self.add(key, val)
			else:
				for (key, val) in items:
					self.add(key, val)

	def __post_init__(self):
		super(AVL_Dict, self).__init__()
		self.n = 0
		self.root = None

	def add(self, key, val):
		'''
		Adds a key-val pair to the tree
		param: key - The key to be inserted
		param: val - The value to which key maps
		'''
		if self.n == 0:
			self.n += 1
			self.root = _Node(key, val)
		else:
			curr = self.root
			traversed_node_list = []

			# Generic BST insertion
			while True:
				traversed_node_list.append(curr)
				if key < curr.key:
					if curr.left is None:
						curr.left = _Node(key, val)
						self.n += 1
						self._fix_heights(traversed_node_list)
						return
					else:
						curr = curr.left
				elif key > curr.key:
					if curr.right is None:
						curr.right = _Node(key, val)
						self.n += 1
						self._fix_heights(traversed_node_list)
						return
					else:
						curr = curr.right
				else:
					curr.key, curr.val = key, val
					# No need to balance since the structure is the same
					return

	def remove(self, key):
		'''
		Removes an item from the tree
		param: key - the key to be deleted
		'''
		if self.root is None:
			raise KeyError(f"Cannot remove from an empty tree!")

		if self.n == 1:
			self.root = None
			self.n = 0
			return

		curr = self.root
		curr_parent = None
		traversed_node_list = []
		while True:
			if curr is None:
				raise KeyError(f"{item=} is not in the tree!")

			traversed_node_list.append(curr)

			if curr.key == key:
				break
			elif key < curr.key:
				curr_parent = curr
				curr = curr.left
			elif curr.key < key:
				curr_parent = curr
				curr = curr.right

		traversed_node_list.pop()
		self.__remove_node(curr, curr_parent, traversed_node_list)
		self._fix_heights(traversed_node_list)
		self.n -= 1



	def __remove_node(self, node, parent, traversed_node_list=None):
		'''
		A method to the node and pass its value to the parent
		param: node - The node we want to delete
		param: parent - The parent node of node
		'''
		if not isinstance(node, _Node):
			raise Exception(f"The node must be of type _Node but is instead {type(node)}")


		if node is None:
			raise Exception(f"The node is None!")

		if parent is None and node is not self.root:
			raise Exception(f"The parent is None!")


		if traversed_node_list is None:
			traversed_node_list = []


		# Case 1: node is leaf
		if node.height == 1:
			if parent.left is node:
				parent.left = None
			elif parent.right is node:
				parent.right = None
			else:
				raise Exception(f"{parent=} isn't a parent of {node=}!")
		# Get smallest element that's bigger than item
		elif node.right is not None:
			traversed_node_list.append(node)
			curr_parent = node
			curr = node.right
			while curr.left is not None:
				traversed_node_list.append(curr)
				curr_parent = curr
				curr = curr.left

			node.key = curr.key
			node.val = curr.val
			self.__remove_node(curr, curr_parent, traversed_node_list)
		elif node.left is not None:
			traversed_node_list.append(node)
			curr_parent = node
			curr = node.left
			while curr.right is not None:
				traversed_node_list.append(curr)
				curr_parent = curr
				curr = curr.right

			node.key = curr.key
			node.val = curr.val
			self.__remove_node(curr, curr_parent, traversed_node_list)





	def get(self, key):
		'''
		Returns the value to which key maps
		param: key - The key whose mapping we'll retreive
		return: val - The value to which key maps 
		'''
		if self.root is None:
			raise KeyError(f"{key=} is not in the tree!")

		curr = self.root
		while True:
			if curr is None:
				raise KeyError(f"{key=} is not in the tree!")

			if curr.key == key:
				return curr.val
			elif key < curr.key:
				curr = curr.left
			else:
				curr = curr.right

	def clear(self):
		'''
		Deletes all of the items in the tree
		'''
		self.root = None
		self.n = 0

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

	def __eq__(self, other):
		if isinstance(other, AVL_Dict) or isinstance(other, dict):
			if len(other) != len(self):
				return False

			for k, v in self.items_yield():
				if k not in other or other[k] != v:
					return False
			return True

		else:
			return False

	def _fix_heights(self, node_list):
		'''
		Balances all of the nodes in node_list
		param: node_list - list of nodes to adjust
		'''
		for i in range(1, len(node_list)):
			if node_list[i - 1].left is not node_list[i] and node_list[i - 1].right is not node_list[i]:
				raise Exception(f"Illegal node traversal! {node_list[i - 1]} is not the parent of {node_list[i]}!")

		if node_list[0] is not self.root:
			raise Exception(f"{node_list[0]=} is not the root!")

		# Calculate the new heights
		for i in range(len(node_list) - 1, -1, -1):
			curr = node_list[i]
			if i > 0:
				self._fix_height(curr, node_list[i-1])
			else:
				self._fix_height(curr)


	def _fix_height(self, node, parent=None):
		'''
		Balances the node so its balance factor is within [-1, 1]
		param: node - the node we'll balance
		param: parent - the parent of node
		'''
		self._calculate_height(node)
		self._calculate_balance(node)
		if node.balance == 2:
			# Scenario 2
			#    node
			#    /  \
			#        x1
			#          \
			#            x2
			if node.right is not None and node.right.balance >= 0:
				if node is self.root:
					self.root = node.right
				else:
					if parent.right is node:
						parent.right = node.right
					elif parent.left is node:
						parent.left = node.right
					# else:
					# 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")

				temp = node.right
				node.right = temp.left
				temp.left = node
				self._calculate_height_and_balance(node)
				self._calculate_height_and_balance(temp.right)
				self._calculate_height_and_balance(temp)
			# Scenario 1
			#    node
			#    /  \
			#        x1
			#       /    
			#      x3      
			# elif node.right is not None and node.right.balance < 0:
			else:
				if node is self.root:
					self.root = node.right.left
				else:
					if parent.left is node:
						parent.left = node.right.left
					elif parent.right is node:
						parent.right = node.right.left
					# else:
					# 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")
				temp = node.right.left
				node.right.left = temp.right
				temp.right = node.right
				node.right = temp.left
				temp.left = node
				self._calculate_height_and_balance(temp.left)
				self._calculate_height_and_balance(temp.right)
				self._calculate_height_and_balance(temp)

			# else:
			# 	raise Exception(f"This node {node} has a perfectly balanced right child!")

		if node.balance == -2:
			# Scenario 4
			#      node
			#     /
			#    x1
			#    /
			#   x2
			if node.left is not None and node.left.balance <= 0:
				if node is self.root:
					self.root = node.left
				else:
					if parent.left is node:
						parent.left = node.left
					elif parent.right is node:
						parent.right = node.left
					# else:
					# 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")

				temp = node.left
				node.left = temp.right
				temp.right = node
				self._calculate_height_and_balance(node)
				self._calculate_height_and_balance(temp.left)
				self._calculate_height_and_balance(temp)
			# Scenario 3
			#    node
			#    /   
			#   x1  
			#     \       
			#      x3   
			else:
				if node is self.root:
					self.root = node.left.right
				else:
					if parent.left is node:
						parent.left = node.left.right
					elif parent.right is node:
						parent.right = node.left.right
					# else:
					# 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")
				temp = node.left.right
				node.left.right = temp.left
				temp.left = node.left
				node.left = temp.right
				temp.right = node
				self._calculate_height_and_balance(temp.right)
				self._calculate_height_and_balance(temp.left)
				self._calculate_height_and_balance(temp)
			# else:
			# 	raise Exception(f"This node {node} has a perfectly balanced left child!")




	def _calculate_height(self, node):
		'''
		Calculates the height of an inputted node
		Note that this assumes that the children have the correct heights
		param: node - node whose height we'll calculate
		'''
		if node is None:
			raise Exception("Can't calculate height on None!")
		if not isinstance(node, _Node):
			raise Exception(f"Passed in node must be _Node but is instead {type(node)}!")

		if node.left is None:
			lh = 0
		else:
			lh = node.left.height
		if node.right is None:
			rh = 0
		else:
			rh = node.right.height

		node.height = max(1 + lh, 1 + rh)

	def _calculate_balance(self, node):
		'''
		Calculates the balance of an inputted node
		Note that this assumes that the children have the correct balances
		param: node - node whose balance we'll calculate
		'''
		if node is None:
			raise Exception("Can't calculate balance on None!")
		if not isinstance(node, _Node):
			raise Exception(f"Passed in node must be _Node but is instead {type(node)}!")

		if node.left is None:
			lh = 0
		else:
			lh = node.left.height
		if node.right is None:
			rh = 0
		else:
			rh = node.right.height

		node.balance = rh - lh

	def _calculate_height_and_balance(self, node):
		self._calculate_height(node)
		self._calculate_balance(node)

	def __contains__(self, key):
		'''
		Tells if you item is in the tree
		param: item - the item to find in the tree
		return: bool - if the item was found in the tree
		'''
		if self.root is None:
			return False

		curr = self.root
		while True:
			if curr is None:
				return False

			if curr.key == key:
				return True
			elif key < curr.key:
				curr = curr.left
			else:
				curr = curr.right


	def __len__(self):
		'''
		Returns the number of items in the tree
		return: int - the number of items in the tree
		'''
		return self.n

	def keys_yield(self):
		'''
		Generator function that iterates DFS through the keys in the tree
		Yields: key - The keys in the tree
		'''
		for key, _ in self.items_yield():
			yield key


	def items_yield(self):
		'''
		Generator function that iterates DFS through the (key, value) pairs in the tree
		Yields: (key, val) - The key value pairs in the tree
		'''
		if self.root is None:
			yield from []
		else:
			discovered = set()
			stack = [self.root]

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
						yield (item.key, item.val)
					inserted = True

				if not inserted:
					item = stack.pop()
					yield (item.key, item.val)

	def __iter__(self):
		'''
		A DFS iterator through the tree
		'''
		self.discovered = set()
		if self.root is None:
			self.stack = []
		else:
			self.stack = [self.root]
		return self

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
					return self.stack.pop(-2).key
				inserted = True

			if not inserted:
				return self.stack.pop().key

		raise StopIteration

	def __dfs_str__(self, node=None):
		if node is None:
			return ''

		result = node.__repr__()


		if node.left is not None:
			result += f", L({self.__dfs_str__(node.left)})"
		if node.right is not None:
			result += f", R({self.__dfs_str__(node.right)})"


		return result

	def __repr__(self):
		if self.root is None:
			return 'AVL_Dict()'
	
		return f"AVL_Dict({self.__dfs_str__(self.root)})"
	
	def __str__(self):
		result = '{'
		l = [f"{key}: {self[key]}" for key in self]
		result += ', '.join(l)
		result += '}'
		return result

	def _verify_itself(self, node=None):
		'''
		Verifies that the tree is balanced
		Should not be called by users
		'''
		if node is None:
			node = self.root
		if self.root is None:
			return

		self._calculate_height_and_balance(node)
		if node.balance < -1 or node.balance > 1:
			raise Exception(f"{node} is a rule breaker!")

		if node.left is not None:
			self._verify_itself(node.left)
		if node.right is not None:
			self._verify_itself(node.right)




def main():

	def random_insertion_test():
		# Random insertions of lists
		# We passed!
		for n in trange(100, 101):
			for x in tqdm(range(10000)):
				t = AVL_Dict()
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
		for x in tqdm(range(10000)):
			t = AVL_Dict()
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
		for x in tqdm(range(10000)):
			t = AVL_Dict()
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
		for n in range(20):
			t = AVL_Dict()
			s = {}
			for x in range(n):
				t[x] = x + 1
				s[x] = x + 1
			pprint(t)
			pprint(s)
			print(t)
			print(s)
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
		for n in trange(0, 100):
			for x in tqdm(range(1000)):
				random.seed(x)
				a = set([(random.randint(0, n), random.randint(0, n)) for x in range(n)])
				t = AVL_Dict(a)
				d = dict(a)

				for k, v in a:
					if k in t:
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
	pprint_test()
	random_mapping_test()
	random_deletion_test()




if __name__ == '__main__':
	main()
