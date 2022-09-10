'''
A multiset that's implemented by using a B-tree
https://en.wikipedia.org/wiki/B-tree

@author: Alfredo Velasco
'''

from collections import defaultdict
from dataclasses import dataclass, field
from List_Heap import List_Heap, get_insertion_index
from pprint import pprint
from tqdm import tqdm
from tqdm.auto import trange
import itertools
import os
import random

global _global_node_id
_global_node_id = 0

@dataclass(order=True)
class _Node(object):
	"""
	A node in the B-tree
	"""

	num_list: List_Heap = field(default_factory=List_Heap)
	children: List_Heap = field(default_factory=List_Heap)
	def __post_init__(self):


		self.num_list = List_Heap(min=False)
		self.children = List_Heap(min=False)
		global _global_node_id
		self._id = _global_node_id
		_global_node_id += 1


	def add(self, item):
		self.num_list.insert(item)

	def _add_child(self, new_child):
		self.children.insert(new_child)

	def __contains__(self, item):
		return item in self.num_list

	def pop(self, index=None):
		if index is None:
			return self.num_list.pop()
		return self.num_list.pop(index)

	def _pop_child(self, index=None):
		if index is None:
			return self.children.pop()
		else:
			return self.children.pop(index)

	def is_leaf(self):
		return len(self.children) == 0

	def is_under_fertile(self):
		return len(self.children) < len(self.num_list) + 1

	def __len__(self):
		return len(self.num_list)

	def __getitem__(self, index):
		return self.num_list.__getitem__(index)

@dataclass
class BTree(object):
	"""
	A multiset that's implemented using a B-tree
	"""

	# The degree of the tree
	_b: int = 3
	# The root of the tree
	_root: _Node = None

	def __init__(self, b=3, items=None):

		if not isinstance(b, int):
			raise Exception(f"b should be an int but is instead {type(b)}!")

		if self._b < 2:
			raise Exception(f"Invalid {self._b=} specified! It must be at least 2!")	

		self._root = _Node()
		self._n = 0

		if items is not None:
			self.add_items(items)

	def add_items(self, l):
		'''
		Add a list of items to the tree

		:param l: the list of items to insert
		'''
		for index, i in enumerate(l):
			self.add(i)

	def add(self, item):
		'''
		Adds an item to the tree

		:param item: the item to insert
		'''

		root = self._root
		curr = root
		visited_list = [root]
		while not curr.is_leaf():
			curr = curr.children[get_insertion_index(item, curr.num_list)]
			visited_list.append(curr)

		curr.add(item)

		if len(curr.num_list) > self._b:
			self._rebalance(visited_list)
		self._n += 1

	def _rebalance(self, visited_list):
		'''
		Rebalances the tree along the visited_list path

		:param list(_Node) visited_list: the list of nodes visited during an insertion/deletion
		'''

		if visited_list[0] is not self._root:
			raise Exception(f"This {visited_list=} should have the root as the first element!")

		while visited_list and len(visited_list[-1]) > self._b:
			curr = visited_list[-1]
			new_node = _Node()

			for i in range(self._b // 2):
				new_node.add(curr.pop())

			if not curr.is_leaf():
				while new_node.is_under_fertile():
					new_node._add_child(curr._pop_child())


			parent = None
			if curr is self._root:
				parent = _Node()
				self._root = parent
				parent._add_child(curr)
			else:
				parent = visited_list[-2]

			parent.add(curr.pop())

			parent._add_child(new_node)
			visited_list.pop()

			if len(parent.children) != len(parent) + 1:
				raise Exception(f"{parent}")

		while visited_list and len(visited_list[-1]) == 0:
			curr = visited_list[-1]
			if curr is self._root:
				self._root = curr.children[0]
				return
			parent = visited_list[-2]

			curr_index = parent.children.index(curr)
			# If we can take from the left sibling
			if curr_index > 0 and len(parent.children[curr_index - 1]) > 1:
				sibling = parent.children[curr_index - 1]
				curr.add(parent.pop(curr_index - 1))
				parent.add(sibling.pop())
				while not sibling.is_leaf() and curr.is_under_fertile():
					curr._add_child(sibling._pop_child())

			# If we can take from the right sibling
			elif curr_index < len(parent) and len(parent.children[curr_index + 1]) > 1:
				sibling = parent.children[curr_index + 1]
				curr.add(parent.pop(curr_index))
				parent.add(sibling.pop(0))
				while not sibling.is_leaf() and curr.is_under_fertile():
					curr._add_child(sibling._pop_child(0))

			else:
				# Merge with left sibling
				if curr_index > 0:
					sibling = parent.children[curr_index - 1]
					sibling.add(parent.pop(curr_index - 1))
				# If we can take from the right sibling
				elif curr_index < len(parent):
					sibling = parent.children[curr_index + 1]
					sibling.add(parent.pop(curr_index))

				while not sibling.is_leaf() and sibling.is_under_fertile():
					sibling._add_child(curr._pop_child())

				parent.children.pop(curr_index)

			visited_list.pop()


	def clear(self):
		self._root = _Node()
		self._n = 0

	def remove(self, item):
		'''
		Removes item from the multiset
	
		:param item: the item to remove
		:raises Exception: if item is not in the tree
		'''

		curr = self._root
		visited_list = [self._root]
		while item not in curr:
			if curr is None or len(curr.children) == 0:
				raise Exception(f"Item {item} is not in the tree!")

			curr = curr.children[get_insertion_index(item, curr.num_list)]
			visited_list.append(curr)

		if curr.is_leaf():
			curr.num_list.remove(item)
		else:
			replace_curr = curr.children[curr.num_list.index(item)]
			visited_list.append(replace_curr)

			while not replace_curr.is_leaf():
				replace_curr = replace_curr.children[-1]
				visited_list.append(replace_curr)
			curr.num_list.remove(item)
			curr.add(replace_curr.num_list.pop())
			


		self._n -= 1
		if len(visited_list[-1]) == 0 and self._n > 0:
			self._rebalance(visited_list)






	def __len__(self):
		return self._n

	def __iter__(self):
		'''
		A DFS iterator through the tree
		'''
		self.discovered = set()
		if self._root is None:
			self.stack = []
		else:
			self.stack = [ (self._root, 0) ]
		return self

	def __next__(self):

		while self.stack:
			node, item_index = self.stack[-1]
			# print(f"{node=} {item_index=}")

			self.discovered.add(node._id)
			# print(f"{self.discovered=}")

			added_child = False
			for i, child in enumerate(node.children):
				if child._id in self.discovered:
					if item_index == i and i < len(node.num_list):
						self.stack[-1] = (node, item_index + 1)
						# print(f"Returning {node.num_list[i]}")
						return node.num_list[i]
					else:
						continue
				self.stack.append( (child, 0) )
				self.discovered.add(child._id)
				added_child = True
				# print(f"Adding {child=} 0")
				break

			if not added_child:
				if item_index < len(node.num_list):
					# print(f"Returning {node.num_list[item_index]}")
					self.stack[-1] = (node, item_index + 1)
					return node.num_list[item_index]
				else:
					self.stack.pop()

		raise StopIteration


	def __repr__(self):
		'''
		Returns a graphical representation of the tree
		'''

		if self._root is None:
			return ''
		
		self.discovered = set()

		# node, level, item index
		self.stack = [ (self._root, 0, 0) ]
		y = 0
		# Each item maps to a list of coordinates in the terminal
		item_to_coords = defaultdict(list)
		# Each level of the tree has a minimum width needed to hold all of its elements
		level_to_width = defaultdict(int)

		# DFS to get all of the elements and their coordinates
		while self.stack:
			node, level, item_index = self.stack[-1]

			self.discovered.add(node._id)

			added_child = False
			for i, child in enumerate(node.children):
				if child._id in self.discovered:
					if item_index == i and i < len(node.num_list):
						self.stack[-1] = (node, level + 1, item_index + 1)

						added_child = False
						break
					else:
						continue
				self.stack.append( (child, level + 1, 0) )
				self.discovered.add(child._id)
				added_child = True
				break

			if not added_child:
				if item_index < len(node.num_list):

					self.stack[-1] = (node, level, item_index + 1)

					item = node.num_list[item_index]
					item_to_coords[item].append( (y, level) )
					if level == 0:
						level_to_width[level] = max(level_to_width[level], len(str(item)))
					else:
						level_to_width[level] = max(len(str(item)) + 3 + level_to_width[level - 1], level_to_width[level])

					y += 1
				else:
					self.stack.pop()

		# pprint(item_to_coords)
		# pprint(level_to_width)


		def replace_2d_str(M, element, row, col):
			'''
			Replaces the items in a 2D array M with the characters of element in position row,col

			example
			M = #####
				#####
				#####
				#####
			
			replace_2d_str(M, 'abc', 1, 2)

			M = #####
				##abc
				#####
				#####

			'''
			element_str = str(element)

			for i in range(len(element_str)):
				M[row][col + i] = element_str[i]

		
		# Set a 2D representation of the output string
		# Each element is a character that will be printed to the screen
		x = max(level_to_width.values()) - 1
		result = []
		for i in range(y):
			result.append([])
			for j in range(x):
				result[-1].append(' ')

		for item in item_to_coords:
			for coor in item_to_coords[item]:
				replace_2d_str(result, item, coor[0], level_to_width[coor[1] - 1])

		# We want to elements to increase as we scroll up so we need to reverse the lines
		result.reverse()
		return '\n'.join([''.join(x) for x in result])

	def __str__(self):
		l = [f"{item}" for item in self ]
		return '[' + ', '.join(l) + ']'


	def to_dot(self, f_name):
		'''
		This method writes out the B-tree to a .dot file so that it can be visualized by graphviz

		:param str f_name: the name of the file where the output will be printed
		:raises Exception: if f_name has a non .dot extension
		'''

		filen, file_ext = os.path.splitext(f_name)

		if file_ext != '.dot' and file_ext != '':
			raise Exception(f"{f_name=} must end with .dot if it has an extension!")

		file_ext = '.dot'
		f_name = f"{filen}{file_ext}"

		with open(f_name, 'w') as f:
			f.write("digraph BTree{\n")
			f.write('node[fontname="Helvetica,Arial,sans-serif",shape=box]\n')
			f.write('layout=dot\n')
			f.write('rankdir=UD\n')

			if self._root is not None:
				node_to_index = {}
				index = 0
				discovered = set()
				stack = [self._root]

				while stack:
					node = stack.pop()
					if node is None:
						raise Exception("This tree has a None element!")
					if not isinstance(node, _Node):
						raise Exception("This tree has a non-_Node {node} element!")
					
					node_id = id(node)
					discovered.add(node_id)
					if node_id not in node_to_index:
						node_to_index[node_id] = index
						index += 1
					f.write(f'\tn{node_to_index[node_id]}[label="{node.num_list}"]\n')


					for child in node.children:
						child_node_id = id(child)
						if child_node_id in discovered:
							continue
						node_to_index[child_node_id] = index
						index += 1
						f.write(f'\tn{node_to_index[node_id]} -> n{node_to_index[child_node_id]}\n')
						
						stack.append(child)
						inserted_left = True
						inserted = True



			f.write('}\n')







def main():
	
	# Random insertions of lists
	#
	def random_insertion_test():
		for n in trange(2, 20, desc='Size loop'):
			for x in tqdm(range(1000), desc='Insertion'):
				s = list(range(1000))
				l = s[:]
				random.seed(x)
				random.shuffle(l)
				t = BTree(n, l)
				r = list(t)

				if r != s:
					raise Exception(f"{x=} results in an error!")

				if len(r) != len(s):
					raise Exception(f"{x=} results in an error!")

	# Random duplicates
	#
	def random_duplicate_test():
		for n in trange(2, 20, desc='Size loop'):
			for x in tqdm(range(1000), desc='Duplicates'):
				random.seed(x)
				l = [random.randint(1, 10) for x in range(10)]
				s = l[:]
				t = BTree(n)
				t.add_items(l)
				s.sort()
				r = list(t)
				if r != s:
					raise Exception(f"{x=} results in an error!\n{r}\n{s}")
				if len(r) != len(s):
					raise Exception(f"{x=} results in an error!")


	# Check the contains
	#
	def contains_test():
		for n in tqdm([2, 15, 20], desc='Size loop'):
			for x in tqdm(range(100), desc='Contains'):
				random.seed(x)
				s = set(random.sample(list(range(1000)), 100))
				c = set(range(1000)) - s

				t = BTree(n, s)
				for i in s:
					if i not in t:
						raise Exception(f"{x=} causes an error!")
				for i in c:
					if i in t:
						raise Exception(f"{x=} causes an error!")

	def remove_test():
		# Test the remove method
		# 
		for n in tqdm(list(itertools.chain(range(20), [50, 100])), desc='Size'):
			t = BTree(n)
			for x in tqdm(range(10000), desc='Remove'):
				t.clear()
				random.seed(x)
				a = set([random.randint(0, n) for x in range(n)])
				b = set([random.randint(0, n) for x in range(n)])
				
				t.add_items(a)

				# print(t)
				for i in b:
					if i in t:
						t.remove(i)

				s = a - b
				r = set(t)
				if r != s:
					raise Exception(f"{x=} results in an error!\n{r}\n{s}")
				if len(r) != len(s):
					raise Exception(f"{x=} results in an error!")

	
	random_insertion_test()
	random_duplicate_test()
	contains_test()
	remove_test()










if __name__ == '__main__':
	b = BTree(3, range(100))

	pprint(b)
