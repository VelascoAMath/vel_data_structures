'''

A set that is implemented using an AVL tree
https://en.wikipedia.org/wiki/AVL_tree

@author: Alfredo Velasco
'''

from dataclasses import dataclass, field
from pprint import pprint
import itertools
import random
from tqdm import tqdm
from tqdm.auto import trange
from collections import deque, defaultdict
import os
from AVL import AVL, _Node


@dataclass
class AVL_Set(AVL):
	"""Represents an AVL tree"""

	def __init__(self, items=None, fast_insert=True):
		'''
		Initializes the tree with the items (if provided)

		:param list( items ) items: list of items to insert into the tree
		:param bool fast_insert: whether or not to sort the list of items in order to quickly build the tree at the cost of increasing the memory requirements
		'''
		super(AVL_Set, self).__init__()

		if items is not None:
			if fast_insert:
				l = list(set(items))
				l.sort()
				self.add_sorted(l)
			else:
				self.add_items(items)

		

	def add(self, item):
		'''
		Adds an item to the tree unless it's already in here (then we ignore it)

		:param item: the item to be inserted
		'''
		if self._n == 0:
			self._root = _Node( item )
		else:
			self._find_deletion_point( item )
			curr = self._traversed_node_list[-1]

			if curr.item == item:
				return
			elif item < curr.item and curr.left is None:
				curr.left = _Node(item=item)
			elif curr.item < item and curr.right is None:
				curr.right = _Node(item=item )
			else:
				raise Exception(f"{self=} {item=}\nI didn't think about this situation!")
			self._fix_heights(self._traversed_node_list)
		self._n += 1
		self._traversed_node_list = []

	def add_items(self, l):
		'''
		Add a list of items to the tree

		:param l: the list of items to insert
		'''
		for i in l:
			self.add(i)

	def add_sorted(self, l):
		'''
		Lets us insert a collection of sorted items quickly when the tree is being initialized

		:param l: the list of items to insert
		:raises Exception: if l is not sorted or has duplicates
		:raises Exception: if the tree is not empty
		'''
		if self._n != 0:
			raise Exception("We can only quickly add sorted items into an empty tree!")

		if not l:
			return

		for i in range(1, len(l)):
			if l[i - 1] > l[i]:
				raise Exception(f"{l=} is not sorted!")
			elif l[i - 1] == l[i]:
				raise Exception(f"{l=} has duplicates at index {i}")

		super(AVL_Set, self).add_sorted(l)



	def __repr__(self):
		if self._root is None:
			return 'AVL_Set()'

		return f"AVL_Set(\n{self.__terminal_str__()})"


	def to_dot(self, f_name):
		'''

		   This method writes out the AVL to a .dot file so that it can be visualized by graphviz.

		   :param str f_name: the name of the files
		   :raises Exception: if the f_name has a non .dot extension
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

			if self._root is not None:
				stack = [(self._root, 0)]

				while stack:
					node, node_id = stack.pop()

					if node is None:
						raise Exception("This tree has a None element!")
					if not isinstance(node, _Node):
						raise Exception("This tree has a non-_Node {node} element!")
					
					f.write(f'\tn{node_id}[shape=circle, label="{node.item}"]\n')



					if node.left is not None:
						l_node_id = node_id + 1
						f.write(f'\tn{node_id} -> n{l_node_id} [color="red"]\n')
						
						stack.append( (node.left, l_node_id) )

					if node.right is not None:
						# The left subtree can only contain at most 2 ^ (node.height - 1) nodes
						r_node_id = node_id + (1 << (node.height - 1) )
						f.write(f'\tn{node_id} -> n{r_node_id} [color="blue"]\n')

						stack.append( (node.right, r_node_id) )



			f.write('}\n')




	def _verify_itself(self, node=None):
		'''
		Verifies that the tree is balanced, ordered, and has the correct balance factor and height
		'''
		if node is None:
			node = self._root
		if self._root is None:
			return

		prev_balance = node.balance
		prev_height = node.height


		if node.left is not None:
			if node.left.item >= node.item:
				raise Exception(f"{node} >= {node.left} (its left child)!")
			self._verify_itself(node.left)
		if node.right is not None:
			if node.right.item <= node.item:
				raise Exception(f"{node} >= {node.right} (its right child)!")
			self._verify_itself(node.right)

		self._calculate_height_and_balance(node)
		
		if node.balance != prev_balance:
			raise Exception(f"{node} should have a balance of {node.balance}!")
		if node.height != prev_height:
			raise Exception(f"{node} should have a height of {node.height}!")
		if node.balance < -1 or node.balance > 1:
			raise Exception(f"{node} should have a balance in [-1, 1]!")




def main():

	# t = AVL_Set(list(range(512 - 1)))
	# t.to_dot('Trash')
	# return

	# Random insertions of lists
	#
	def random_insertion_test():
		for x in tqdm(range(10000), desc='Insertion'):
			s = list(range(100))
			l = s[:]
			random.seed(x)
			random.shuffle(l)
			t = AVL_Set(l, False)
			r = list(t)

			if r != s:
				raise Exception(f"{x=} results in an error!")

			if len(r) != len(s):
				raise Exception(f"{x=} results in an error!")



	# Random duplicates
	#
	def random_duplicate_test():
		for x in tqdm(range(10000), desc='Duplicates'):
			random.seed(x)
			l = [random.randint(1, 100) for x in range(1000)]
			s = set(l)
			t = AVL_Set()
			t.add_items(l)
			t._verify_itself()
			r = set(t)
			if r != s:
				raise Exception(f"{x=} results in an error!\n{r}\n{s}")
			if len(r) != len(s):
				raise Exception(f"{x=} results in an error!")

		for x in tqdm(range(1000), desc='Duplicates'):
			random.seed(x)
			l = list(set([random.randint(1, 100) for x in range(1000)]))
			l.sort()
			s = set(l)
			t = AVL_Set(l)
			t._verify_itself()
			r = set(t)
			if r != s:
				raise Exception(f"{x=} results in an error!\n{r}\n{s}")
			if len(r) != len(s):
				raise Exception(f"{x=} results in an error!")



	# Check the contains
	#
	def contains_test():
		for x in tqdm(range(10000), desc='Contains'):
			random.seed(x)
			s = set(random.sample(list(range(1000)), 100))
			c = set(range(1000)) - s

			t = AVL_Set(s, True)
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
			t = AVL_Set()
			for x in tqdm(range(10000), desc='Remove'):
				t.clear()
				random.seed(x)
				a = set([random.randint(0, n) for x in range(n)])
				b = set([random.randint(0, n) for x in range(n)])
				
				t.add_items(a)
				t._verify_itself()

				# print(t)
				for i in b:
					if i in t:
						t.remove(i)
						t._verify_itself()

				s = a - b
				r = set(t)
				if len(r) != len(s):
					raise Exception(f"{x=} results in an sets of different lengths!\n{r}\n{s}")
				if r != s:
					raise Exception(f"{x=} results in an error!\n{r}\n{s}")
		

		# Test the remove method
		# 
		for n in tqdm([1000, 10000], desc='Size'):
			t = AVL_Set()
			for x in tqdm(range(1000 // n), desc='Remove'):
				t.clear()
				random.seed(x)
				a = set([random.randint(0, n) for x in range(n)])
				b = set([random.randint(0, n) for x in range(n)])
				
				t.add_sorted(sorted(list(a)))
				t._verify_itself()

				for i in b:
					if i in t:
						t.remove(i)
						t._verify_itself()

				s = a - b
				r = set(t)
				if len(list(t)) != len(s):
					raise Exception(f"{x=} results in an sets of different lengths!\n{r}\n{s}")
				if r != s:
					raise Exception(f"{x=} results in an error!\n{r}\n{s}")
	
	random_insertion_test()
	random_duplicate_test()
	contains_test()
	remove_test()







if __name__ == '__main__':
	main()
