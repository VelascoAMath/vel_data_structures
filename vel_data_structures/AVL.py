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
import os

@dataclass
class _Node(object):
	"""docstring for _Node"""

	item:    int = None
	height:  int = 1
	balance: int = 0
	left:    int = None
	right:   int = None

	def __repr__(self):
		return f"{self.item=} {self.height=} {self.balance=}"



@dataclass
class AVL(object):
	"""Represents an AVL tree"""

	n: int = 0
	root: _Node = field(default_factory=_Node)

	def __init__(self, items=None):
		self.__post_init__()

		if items is not None:
			for item in items:
				self.add(item)

	def __post_init__(self):
		super(AVL, self).__init__()
		self.n = 0
		self.root = None

	def add(self, item):
		'''
		Adds an item to the tree
		param: item - The item to be inserted
		'''
		if self.n == 0:
			self.n += 1
			self.root = _Node(item)
		else:
			curr = self.root
			traversed_node_list = []

			# Generic BST insertion
			while True:
				traversed_node_list.append(curr)
				if item < curr.item:
					if curr.left is None:
						curr.left = _Node(item)
						self.n += 1
						self._fix_heights(traversed_node_list)
						return
					else:
						curr = curr.left
				else:
					if curr.right is None:
						curr.right = _Node(item)
						self.n += 1
						self._fix_heights(traversed_node_list)
						return
					else:
						curr = curr.right


	def remove(self, item):
		'''
		Removes an item from the tree
		param: item - The item to be deleted
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

			if curr.item == item:
				break
			elif item < curr.item:
				curr_parent = curr
				curr = curr.left
			elif curr.item < item:
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

			node.item = curr.item
			self.__remove_node(curr, curr_parent, traversed_node_list)
		elif node.left is not None:
			traversed_node_list.append(node)
			curr_parent = node
			curr = node.left
			while curr.right is not None:
				traversed_node_list.append(curr)
				curr_parent = curr
				curr = curr.right

			node.item = curr.item
			self.__remove_node(curr, curr_parent, traversed_node_list)





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

	def __contains__(self, item):
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

			if curr.item == item:
				return True
			elif item < curr.item:
				curr = curr.left
			else:
				curr = curr.right


	def __len__(self):
		'''
		Returns the number of items in the tree
		return: int - the number of items in the tree
		'''
		return self.n



	def items_yield(self):
		'''
		Generator function that iterates DFS through the items in the tree
		Yields: item - The items in the tree
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
						yield item
					inserted = True

				if not inserted:
					item = stack.pop()
					yield item

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
					return self.stack.pop(-2).item
				inserted = True

			if not inserted:
				return self.stack.pop().item

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
			return 'AVL()'

		return f"AVL({self.__dfs_str__(self.root)})"

	def __str__(self):
		l = [f"{item}" for item in self]
		return '{' + ', '.join(l) + '}'


	def to_dot(self, f_name):
		'''
		This method writes out the AVL to a .dot file so that it can be visualized by graphviz
		param: f_name - the name of the files
		'''

		filen, file_ext = os.path.splitext(f_name)

		if file_ext != '.dot' and file_ext != '':
			raise Exception(f"{f_name=} must end with .dot if it has an extension!")

		file_ext = '.dot'
		f_name = f"{filen}{file_ext}"

		with open(f_name, 'w') as f:
			f.write("digraph AVL{\n")
			f.write('node[fontname="Helvetica,Arial,sans-serif"]\n')
			f.write('layout=dot\n')
			f.write('rankdir=UD\n')

			if self.root is not None:
				node_to_index = {}
				index = 0
				discovered = set()
				stack = [self.root]

				while stack:
					node = stack[-1]
					if node is None:
						raise Exception("This tree has a None element!")
					if not isinstance(node, _Node):
						raise Exception("This tree has a non-_Node {node} element!")
					
					node_id = id(node)
					discovered.add(node_id)
					if node_id not in node_to_index:
						node_to_index[node_id] = index
						index += 1
					f.write(f'\tn{node_to_index[node_id]}[shape=circle, label="{node.item}"]\n')

					inserted_left = False
					inserted = False

					if node.left is not None and id(node.left) not in discovered:
						l_node_id = id(node.left)
						node_to_index[l_node_id] = index
						index += 1
						f.write(f'\tn{node_to_index[node_id]} -> n{node_to_index[l_node_id]}\n')
						
						stack.append(node.left)
						inserted_left = True
						inserted = True

					if not inserted_left and node.right is not None and id(node.right) not in discovered:
						r_node_id = id(node.right)
						node_to_index[r_node_id] = index
						index += 1
						f.write(f'\tn{node_to_index[node_id]} -> n{node_to_index[r_node_id]}\n')

						stack.append(node.right)
						if not inserted:
							item = stack.pop(-2)
							# yield item
						inserted = True

					if not inserted:
						item = stack.pop()
						# yield item


			f.write('}\n')




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

	t = AVL(list(range(512 - 1)))
	t.to_dot('Trash')
	return

	# Test the remove method
	# 
	for n in itertools.chain(range(20), [50, 100]):
		for x in tqdm(range(10000), desc='Remove'):
			t = AVL()
			random.seed(x)
			a = set([random.randint(0, n) for x in range(n)])
			b = set([random.randint(0, n) for x in range(n)])
			for i in a:
				t.add(i)
				t._verify_itself()

			# print(t)
			for i in b:
				if i in t:
					t.remove(i)
					t._verify_itself()

			s = a - b
			r = set(t)
			if r != s:
				raise Exception(f"{x=} results in an error!\n{r}\n{s}")
			if len(r) != len(s):
				raise Exception(f"{x=} results in an error!")
	

	# Test the remove method
	# 
	for n in [1000, 10000]:
		for x in tqdm(range(100000 // n), desc='Remove'):
			t = AVL()
			random.seed(x)
			a = set([random.randint(0, n) for x in range(n)])
			b = set([random.randint(0, n) for x in range(n)])
			for i in a:
				t.add(i)
				t._verify_itself()

			for i in b:
				if i in t:
					t.remove(i)
					t._verify_itself()

			s = a - b
			r = set(t)
			if r != s:
				raise Exception(f"{x=} results in an error!\n{r}\n{s}")
			if len(r) != len(s):
				raise Exception(f"{x=} results in an error!")
	



	# Random insertions of lists
	#
	for x in tqdm(range(10000), desc='Insertion'):
		s = list(range(100))
		l = s[:]
		random.seed(x)
		random.shuffle(l)
		t = AVL(l)
		r = list(t)

		if r != s:
			raise Exception(f"{x=} results in an error!")

		if len(r) != len(s):
			raise Exception(f"{x=} results in an error!")



	# Random duplicates
	#
	for x in tqdm(range(10000), desc='Duplicates'):
		random.seed(x)
		l = [random.randint(1, 100) for x in range(1000)]
		s = l[:]
		t = AVL(l)
		s.sort()
		r = list(t)
		if r != s:
			raise Exception(f"{x=} results in an error!\n{r}\n{s}")
		if len(r) != len(s):
			raise Exception(f"{x=} results in an error!")


	# Check the contains
	#
	for x in tqdm(range(10000), desc='Contains'):
		random.seed(x)
		s = set(random.sample(list(range(1000)), 100))
		c = set(range(1000)) - s

		t = AVL(s)
		for i in s:
			if i not in t:
				raise Exception(f"{x=} causes an error!")
		for i in c:
			if i in t:
				raise Exception(f"{x=} causes an error!")





if __name__ == '__main__':
	main()
