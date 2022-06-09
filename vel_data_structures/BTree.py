'''
A multiset that's implemented by using a B-tree
https://en.wikipedia.org/wiki/B-tree

@author: Alfredo Velasco
'''

from dataclasses import dataclass, field
import random
import os
from tqdm.auto import trange

def get_insertion_index(item, l, reverse=False):
	'''
	Returns the position where item should be inserted so that l stays sorted

	:param item: the item to insert
	:param l: the list where item could be inserted
	:retun index: the index where item would be inserted
	:param reverse=False: whether or not the index should insert the item into l in sorted order or reverse sorted order
	'''

	if len(l) == 0:
		return 0

	if reverse:
		# Insert at the end
		if item <= l[-1]:
			return len(l)

		# Need to insert at the beginning
		if item > l[0]:
			return 0

		# Need to insert in the middle
		for i in range(len(l) - 1, -1, -1):
			if l[i] >= item >= l[i + 1]:
				return i + 1
	else:
		# Insert at the end
		if item < l[0]:
			return 0

		# Need to insert at the beginning
		if l[-1] <= item:
			return len(l)

		# Need to insert in the middle
		for i in range(len(l) - 1, -1, -1):
			if l[i] <= item <= l[i + 1]:
				return i + 1


def insert_into_list(item, l, reverse=False):
	'''
	Inserts item into l in a position that keeps l sorted

	:param item: the item to insert
	:param l: the list where item will be inserted
	:param reverse=False: whether or not we should insert the item into l in sorted order or reverse sorted order
	'''
	l.insert(get_insertion_index(item, l, reverse), item)

@dataclass(order=True)
class _Node(object):
	"""
	A node in the AVL tree
	"""

	num_list: list = field(default_factory=list)
	children: list = field(default_factory=list)
	def __post_init__(self):


		self.children = []


	def add(self, item):
		insert_into_list(item, self.num_list)

	def _add_child(self, new_child):
		insert_into_list(new_child, self.children)

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
	
	def __post_init__(self):
		if self._b < 2:
			raise Exception(f"Invalid {self._b=} specified! It must be at least 2!")

		self._root = _Node()
		self.n = 0

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
		self.n += 1

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
			


		self.n -= 1
		if len(visited_list[-1]) == 0 and self.n > 0:
			self._rebalance(visited_list)






	def __len__(self):
		return self.n

	def to_dot(self, f_name):
		'''
		This method writes out the AVL to a .dot file so that it can be visualized by graphviz

		:param str f_name: the name of the file where the output will be printed
		:raises Exception: if f_name has a non .dot extension
		'''

		filen, file_ext = os.path.splitext(f_name)

		if file_ext != '.dot' and file_ext != '':
			raise Exception(f"{f_name=} must end with .dot if it has an extension!")

		file_ext = '.dot'
		f_name = f"{filen}{file_ext}"

		with open(f_name, 'w') as f:
			f.write("digraph AVL{\n")
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
	for n in trange(2, 20, desc='Size loop'):
		for x in trange(1000, desc='Random loop'):
			a = BTree(n)
			l = list(range(1000))
			random.seed(x)
			random.shuffle(l)
			for i in l:
				a.add(i)
			for i in l:
				a.remove(i)


if __name__ == '__main__':
	main()

