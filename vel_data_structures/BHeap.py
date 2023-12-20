'''
A Binomial Heap
https://en.wikipedia.org/wiki/Binomial_heap

@author: Alfredo Velasco
'''

from tqdm import tqdm, trange
import random
from dataclasses import dataclass, field

@dataclass
class _Tree(object):
	item: int = None
	children: list = field(default_factory=list)
	is_min: bool = True

	def get_k(self):
		'''
		Returns the order of the tree

		:returns int k: the order of the tree
		'''
		if self.children is None:
			return 0
		return len(self.children)

	def merge(self, other):
		'''
		Merges the tree and returns the merged result
	
		:param _Tree other: The other tree we'll merge 
		:returns _Tree result: A merged _Tree
		'''

		if self.get_k() != other.get_k():
			raise Exception("The trees must have the same k! Their ks are {self.get_k()} and {self.get_k()}")

		if self.is_min and self.item < other.item:
			if self.children is None:
				self.children = []
			self.children.append(other)
			return self
		elif not self.is_min and self.item > other.item:
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

	_forest: list = field(default_factory=list)
	_min_heap: _Tree = None
	_n: int = 0
	is_min: bool = True

	def __init__(self, items=None, is_min=True):
		'''
		Initializes the tree with the items (if provided)

		:param list( items ) items: list of items to insert into the tree
		'''
		self._forest = []
		self.is_min = is_min

		if items is not None:
			for item in items:
				self.insert(item)


	def _insert_tree(self, curr):
		'''
		Inserts a new tree into the forest

		:param _Tree curr: the tree to insert
	
		:raises Exception: if curr is not a _Tree
		'''
		if not isinstance(curr, _Tree):
			raise Exception(f"curr must be a tree but is instead {type(curr)}!")

		k = curr.get_k()

		while k >= len(self._forest) or self._forest[k] is not None:
			added_space = False

			while k >= len(self._forest):
				self._forest.append(None)
				added_space = True

			if added_space:
				continue

			curr = curr.merge(self._forest[k])


			self._forest[k] = None

			k = curr.get_k()


		self._forest[k] = curr
		return curr


	def insert(self, item):
		'''
		Inserts an item into the heap

		:param item: the item to insert
		'''
		curr = _Tree(item, is_min=self.is_min)
		self._n += 1

		curr = self._insert_tree(curr)

		if self._min_heap is None or (curr <= self._min_heap and self.is_min) or (curr >= self._min_heap and not self.is_min):
			self._min_heap = curr

	def pop(self):
		'''
		Removes and returns the smallest item from the heap
	
		:returns item: the smallest item in the heap
		:raises Exception: if the heap is empty
		'''
		if self._n <= 0:
			raise Exception("Cannot pop an empty BHeap!")

		item = self._min_heap.item
		self._n -= 1

		k = self._min_heap.get_k()

		children = self._min_heap.children

		self._min_heap = None
		self._forest[k] = None


		while children:
			self._insert_tree(children.pop())

		for tree in self._forest:
			if tree is not None:
				if self._min_heap is None or (self.is_min and tree < self._min_heap) or (not self.is_min and tree > self._min_heap):
					self._min_heap = tree

		return item

	def __len__(self):
		return self._n

	def __bool__(self):
		return self._n > 0






def main():

	def insert_test():
		for n in tqdm(list(range(1, 100)), desc='size loop', smoothing=0):
			for x in trange(10000, desc='random loop'):
				random.seed(x)
				a = set([random.randint(-n, n) for x in range(n)])
				b = BHeap(a)

				if min(a) != b._min_heap.item:
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong minimum! We found {b=} instead of {min(a)}")

				if len(b) != len(a):
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong length! We found {len(b)=} instead of {len(a)}")
		for n in tqdm(list(range(1, 100)), desc='size loop', smoothing=0):
			for x in trange(10000, desc='random loop'):
				random.seed(x)
				a = set([random.randint(-n, n) for x in range(n)])
				b = BHeap(a, is_min=False)

				if max(a) != b._min_heap.item:
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong minimum! We found {b=} instead of {max(a)}")

				if len(b) != len(a):
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong length! We found {len(b)=} instead of {len(a)}")

	def sort_test():
		n = 10000
		for x in tqdm(list(range(10000)), desc='size loop', smoothing=0):
			random.seed(x)
			a = list([random.randint(-n, n) for x in range(n)])
			b = BHeap(a)
			a.sort()
			s = []

			i = n - 1
			while b:
				s.append(b.pop())
				if len(b) != i:
					raise Exception("NO")
				i -= 1

			if a != s:
				raise Exception("{x=} causes an error!")

		for x in tqdm(list(range(10000)), desc='size loop', smoothing=0):
			random.seed(x)
			a = list([random.randint(-n, n) for x in range(n)])
			b = BHeap(a, is_min=False)
			a.sort(reverse=True)
			s = []

			i = n - 1
			while b:
				s.append(b.pop())
				if len(b) != i:
					raise Exception("NO")
				i -= 1

			if a != s:
				raise Exception("{x=} causes an error!")

	insert_test()
	sort_test()


if __name__ == '__main__':
	main()

