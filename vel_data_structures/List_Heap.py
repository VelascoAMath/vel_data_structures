from dataclasses import dataclass, field
from tqdm import tqdm, trange
import random

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


@dataclass
class List_Heap(object):

	item_list: list = field(default_factory=list)

	"""docstring for List_Heap"""
	def __init__(self, item_list=None, fast_insert=True, min=True):
		super(List_Heap, self).__init__()
		self.item_list = []
		self.min = min

		if item_list is not None:
			if fast_insert:
				l = list(item_list)
				l.sort(reverse=min)
				self.item_list = l
			else:
				for item in item_list:
					self.insert(item)


	def insert(self, item):
		insert_into_list(item, self.item_list, self.min)


	def pop(self, index=None):
		if not self.item_list:
			raise Exception("Cannot pop an empty List_Heap!")

		if index is not None:
			return self.item_list.pop(index)
		return self.item_list.pop()

	def index(self, item):
		return self.item_list.index(item)

	def remove(self, item):
		self.item_list.remove(item)

	def __getitem__(self, key):
		return self.item_list[key]

	def __gt__(self, other):
		if isinstance(other, List_Heap):
			return self.item_list > other.item_list
		raise Exception("Comparison only supported between List_Heap objects!")

	def __ge__(self, other):
		if isinstance(other, List_Heap):
			return self.item_list >= other.item_list
		raise Exception("Comparison only supported between List_Heap objects!")

	def __lt__(self, other):
		if isinstance(other, List_Heap):
			return self.item_list < other.item_list
		raise Exception("Comparison only supported between List_Heap objects!")

	def __le__(self, other):
		if isinstance(other, List_Heap):
			return self.item_list <= other.item_list
		raise Exception("Comparison only supported between List_Heap objects!")

	def __len__(self):
		return len(self.item_list)

	def __bool__(self):
		return bool(self.item_list)
		




def main():
	def insert_test():
		for n in tqdm(random.sample(list(range(1, 100)), 99), desc='size loop', smoothing=0):
			for x in trange(10000, desc='random loop'):
				random.seed(x)
				a = set([random.randint(-n, n) for x in range(n)])
				b = List_Heap(a)

				if min(a) != b.item_list[-1]:
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong minimum! We found {b=} instead of {min(a)}")

		for n in tqdm(list(range(1, 100)), desc='size loop', smoothing=0):
			for x in trange(10000, desc='random loop'):
				random.seed(x)
				a = set([random.randint(-n, n) for x in range(n)])
				b = List_Heap(a, False)

				if min(a) != b.item_list[-1]:
					print(f"Adding {a=} and we have {b=}")
					raise Exception(f"{n=} {x=} provides us the wrong minimum! We found {b=} instead of {min(a)}")

	def sort_test():
		n = 10000
		for x in tqdm(list(range(10000)), desc='size loop', smoothing=0):
			random.seed(x)
			a = list([random.randint(-n, n) for x in range(n)])
			b = List_Heap(a)
			a.sort()
			s = []

			while b:
				s.append(b.pop())

			if a != s:
				raise Exception("{x=} causes an error!")

	insert_test()
	sort_test()


if __name__ == '__main__':
	main()