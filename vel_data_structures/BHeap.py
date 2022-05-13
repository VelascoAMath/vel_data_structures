'''
A Binomial Heap

@author: Alfredo Velasco
'''

from tqdm import tqdm, trange
import random
from dataclasses import dataclass, field

@dataclass
class Tree(object):
	item: int = None
	children: list = field(default_factory=list)

	# def __init__(self, item):
	# 	self.item = item
	# 	self.children = None

	def get_k(self):
		if self.children is None:
			return 0
		return len(self.children)

	def merge(self, other):
		if self.get_k() != other.get_k():
			raise Exception("The trees must have the same k! Their ks are {self.get_k()} and {self.get_k()}")

		if self.item < other.item:
			if self.children is None:
				self.children = []
			self.children.append(other)
			return self
		else:
			if other.children is None:
				other.children = []
			other.children.append(self)
			return other

	def __lt__(self, other):
		return self.item < other.item

	def __ge__(self, other):
		return self.item >= other.item

@dataclass
class BHeap(object):

	forest: list = field(default_factory=list)
	min_heap: Tree = None
	n: int = 0

	def __init__(self, items=None):

		self.forest = []

		if items is not None:
			for item in items:
				self.insert(item)


	def insert_tree(self, curr):

		if not isinstance(curr, Tree):
			raise Exception(f"curr must be a tree but is instead {type(curr)}!")

		k = curr.get_k()

		while k >= len(self.forest) or self.forest[k] is not None:
			added_space = False

			while k >= len(self.forest):
				self.forest.append(None)
				added_space = True

			if added_space:
				continue

			curr = curr.merge(self.forest[k])


			self.forest[k] = None

			k = curr.get_k()


		self.forest[k] = curr


	def insert(self, item):
		curr = Tree(item)
		self.n += 1

		self.insert_tree(curr)

		if self.min_heap is None or curr < self.min_heap:
			self.min_heap = curr

	def pop(self):

		if self.n <= 0:
			raise Exception("Cannot pop an empty BHeap!")

		item = self.min_heap.item
		self.n -= 1

		k = self.min_heap.get_k()

		children = self.min_heap.children

		self.min_heap = None
		self.forest[k] = None


		while children:
			self.insert_tree(children.pop())

		for tree in self.forest:
			if tree is not None:
				if self.min_heap is None or tree < self.min_heap:
					self.min_heap = tree

		return item


	def __bool__(self):
		return self.n > 0
	# def __str__(self):
	# 	return str(self.forest)





def main():

	def insert_test():
		# for n in tqdm(random.sample(list(range(1, 100)), 99), desc='size loop', smoothing=0):
		for n in tqdm(list(range(1, 100)), desc='size loop', smoothing=0):
			for x in trange(10000, desc='random loop'):
				random.seed(x)
				a = set([random.randint(-n, n) for x in range(n)])
				b = BHeap(a)

				if min(a) != b.min_heap.item:
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong minimum! We found {b=} instead of {min(a)}")

	def sort_test():
		n = 10000
		for x in tqdm(list(range(10000)), desc='size loop', smoothing=0):
			random.seed(x)
			a = list([random.randint(-n, n) for x in range(n)])
			b = BHeap(a)
			a.sort()
			s = []

			while b:
				s.append(b.pop())

			if a != s:
				raise Exception("{x=} causes an error!")

	# insert_test()
	sort_test()


if __name__ == '__main__':
	main()