import itertools
import random
import time
from pprint import pprint

import optuna
from tqdm import tqdm


def _partition(a, pivot_index=None, lo=None, hi=None):
	'''
	lo: the inclusive lower index of the range one wishes to partition
	hi: the exclusive higher index of the range one wishes to partition
	'''
	def swap(l, i, j):
		temp = l[i]
		l[i] = l[j]
		l[j] = temp

	# Empty and singular arrays are partitioned already
	if len(a) <= 1:
		return 0

	if hi is None:
		hi = len(a)
	if lo is None:
		lo = 0

	# Empty and singular arrays are already partitioned
	if hi - lo <= 1:
		return lo

	if pivot_index is None:
		pivot_index = hi - 1
	else:
		swap(a, hi-1, pivot_index)
		pivot_index = hi - 1
	pivot = a[pivot_index]

	i = lo
	j = hi - 2

	while True:
		# Find some elements whose order is reversed
		while i < pivot_index and a[i] <= pivot:
			i += 1
		while j > 0 and pivot <= a[j]:
			j -= 1

		# Done. Just need to play the pivot in place
		if i >= j:
			swap(a, i, pivot_index)
			return i

		# No issue. Let's move on
		if a[i] <= pivot and pivot <= a[j]:
			i += 1
			j -= 1
		# Reversed positions
		elif a[j] < pivot and pivot < a[i]:
			swap(a, i, j)
			i += 1
			j += 1


def partition_test():
	random.seed(2)
	for size in tqdm(range(10 + 1)):
		l = list(range(1, size + 1))
		for x in itertools.permutations(l):
			a = list(x)
			pivot_index = _partition(a)
			if len(a) > 0:
				pivot = a[pivot_index]
				for i in range(pivot_index):
					if a[i] > pivot:
						raise Exception(f"{pivot_index=} {pivot=} {x=} {i=} {a=}")
				for i in range(pivot_index + 1, len(a)):
					if a[i] < pivot:
						raise Exception(f"{pivot_index=} {pivot=} {x=} {i=} {a=}")


# https://en.wikibooks.org/wiki/Algorithm_Implementation/Sorting/Insertion_sort#Python
def insertion_sort(array, lo=None, hi=None):
	if lo is None: lo = 1
	if hi is None: hi = len(array)

	for removed_index in range(lo, hi):
		removed_value = array[removed_index]
		insert_index = removed_index
		while insert_index > 0 and array[insert_index - 1] > removed_value:
			array[insert_index] = array[insert_index - 1]
			insert_index -= 1
		array[insert_index] = removed_value

def quicksort(a, lo=None, hi=None, lb=None, ub=None, insert_size=10):
	if (len(a) <= 1):
		return
	if lo is None:
		lo = 0
	if hi is None:
		hi = len(a)

	if hi - lo <= 1:
		return

	if lb is None:
		lb = 0
	if ub is None:
		ub = hi

	pivot = a[hi-1]
	if hi - lo < insert_size:
		(_, pivot_index) = insertion_sort(a, lo, hi)
	else:
		_partition(a, lo, hi)

	if( lo < pivot_index and pivot_index > lb):
		quicksort(a, lo, pivot_index, lb, ub)
	if (pivot_index < hi and pivot_index < ub):
		quicksort(a, pivot_index, hi, lb, ub)


def quicksort_test():
	for size in tqdm(range(10 + 1)):
		l = list(range(1, size + 1))
		for x in itertools.permutations(l):
			a = list(x)
			quicksort(a)
			if len(a) > 1:
				for i in range(1, len(a)):
					if a[i - 1] > a[i]:
						raise Exception(f"{size=} {x=} {a=}")


def main():
	a = list(range(50))
	random.shuffle(a)

	print(a)
	quicksort(a, lb=20, ub=30)
	print(a)

if __name__ == '__main__':
	# partition_test()
	# quicksort_test()
	main()
