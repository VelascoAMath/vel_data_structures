import itertools
import random

from tqdm import tqdm


def _partition(a, lo=None, hi=None):
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
		return

	if hi is None:
		hi = len(a)
	if lo is None:
		lo = 0

	# Empty and singular arrays are already partitioned
	if hi - lo <= 1:
		return

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
			return

		# No issue. Let's move on
		if a[i] <= pivot and pivot <= a[j]:
			i += 1
			j -= 1
		# Reversed positions
		elif a[j] < pivot and pivot < a[i]:
			swap(a, i, j)
			i += 1
			j += 1


def quick_select(a, i, lo=None, hi=None):
	if (len(a) == 0):
		return None
	if (len(a) == 1):
		return a[0]

	if lo is None:
		lo = 0
	if hi is None:
		hi = len(a)

	if hi == lo: return None
	if hi - lo == 1:
		return a[lo]

	pivot = a[hi-1]
	_partition(a, lo, hi)
	pivot_index = a.index(pivot)
	if( pivot_index < i):
		return quick_select(a, i, pivot_index, hi)
	elif (i < pivot_index):
		return quick_select(a, i, lo, pivot_index)
	else:
		return pivot



def main():
	for size in tqdm(range(10)):
		for x in itertools.permutations(range(size)):
			a = list(x)
			for i in range(len(a)):
				answer = quick_select(a, i)
				if answer != i:
					raise Exception(f"{x} {a} {i} {answer}")

if __name__ == '__main__':
    main()