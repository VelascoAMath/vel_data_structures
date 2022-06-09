from tqdm import tqdm, trange
import random
from BTree import insert_into_list
from dataclasses import dataclass, field

@dataclass
class List_Heap(object):

	item_list: list = field(default_factory=list)

	"""docstring for List_Heap"""
	def __init__(self, item_list=None, fast_insert=True):
		super(List_Heap, self).__init__()
		self.item_list = []

		if item_list is not None:
			if fast_insert:
				l = list(item_list)
				l.sort(reverse=True)
				self.item_list = l
			else:
				for item in item_list:
					self.insert(item)


	def insert(self, item):
		insert_into_list(item, self.item_list, True)


	def pop(self):
		if not self.item_list:
			raise Exception("Cannot pop an empty List_Heap!")

		return self.item_list.pop()

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