from dataclasses import dataclass, field
import random
import os
from tqdm.auto import trange

def get_insertion_index(item, l):
	if len(l) == 0 or item < l[0]:
		return 0

	if item < l[0]:
		return 0

	elif l[-1] <= item:
		return len(l)
	else:
		for i in range(0, len(l) - 1):
			if l[i] <= item <= l[i + 1]:
				return i + 1


def insert_into_list(item, l):
	l.insert(get_insertion_index(item, l), item)

@dataclass(order=True)
class _Node(object):
	"""docstring for _Node"""

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
	"""docstring for BTree"""

	b: int = 3
	root: _Node = None
	
	def __post_init__(self):
		if self.b < 2:
			raise Exception(f"Invalid {self.b=} specified! It must be at least 2!")

		self.root = _Node()
		self.n = 0

	def add(self, item):
		root = self.root
		curr = root
		visited_list = [root]
		while not curr.is_leaf():
			curr = curr.children[get_insertion_index(item, curr.num_list)]
			visited_list.append(curr)

		curr.add(item)

		if len(curr.num_list) > self.b:
			self.rebalance(visited_list)
		self.n += 1

	def rebalance(self, visited_list):
		if visited_list[0] is not self.root:
			raise Exception(f"This {visited_list=} should have the root as the first element!")

		while visited_list and len(visited_list[-1]) > self.b:
			curr = visited_list[-1]
			new_node = _Node()

			for i in range(self.b // 2):
				new_node.add(curr.pop())

			if not curr.is_leaf():
				while new_node.is_under_fertile():
					new_node._add_child(curr._pop_child())


			parent = None
			if curr is self.root:
				parent = _Node()
				self.root = parent
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
			if curr is self.root:
				self.root = curr.children[0]
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
		curr = self.root
		visited_list = [self.root]
		while item not in curr:
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
			self.rebalance(visited_list)






	def __len__(self):
		return self.n

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
			f.write('node[fontname="Helvetica,Arial,sans-serif",shape=box]\n')
			f.write('layout=dot\n')
			f.write('rankdir=UD\n')

			if self.root is not None:
				node_to_index = {}
				index = 0
				discovered = set()
				stack = [self.root]

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
			l = list(range(10000))
			random.seed(x)
			random.shuffle(l)
			# print(l)
			for i in l:
				a.add(i)
				# print(a)
			for i in l:
				a.remove(i)
				# print(a)
			# a.to_dot(str(len(a)))


if __name__ == '__main__':
	main()

