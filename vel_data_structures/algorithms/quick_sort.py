import itertools
import os.path
import pickle
import random
import time
from pprint import pprint
import seaborn as sns
import optuna
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt


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
		swap_index = random.randint(lo, hi-1)
		if swap_index != hi - 1:
			swap(a, swap_index, hi-1)
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

def quicksort(a, lo=None, hi=None, lb=None, ub=None, insert_size=28):
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

	if hi - lo <= insert_size:
		insertion_sort(a, lo, hi)
		return
	else:
		pivot_index = _partition(a, lo=lo, hi=hi)

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
	a = list(range(10000))
	random.shuffle(a)

	print(a)
	start = time.time()
	quicksort(a)
	end = time.time()
	print(a)

	print(end - start)


def optimize_selection():
	if os.path.isfile('results.pkl'):
		with open('results.pkl', 'rb') as f:
			results = pickle.load(f)
	else:
		results = {}

	print(results)
	trial_list = list(itertools.product(range(100), range(100)))
	trial_list = [x for x in trial_list if x not in results]
	random.shuffle(trial_list)
	print(trial_list)

	for i, size in tqdm(trial_list):
		try:
			a = list(range(1000000))
			random.seed(i)
			random.shuffle(a)

			start = time.time()
			quicksort(a, insert_size=size)
			end = time.time()
			results[(i, size)] = end - start
		except:
			with open('results.pkl', 'wb') as f:
				pickle.dump(results, f)
			return


	with open('results.pkl', 'wb') as f:
		pickle.dump(results, f)

	data_list = list([tuple([*x, y]) for x, y in results.items()] )
	print(data_list)

	df = pd.DataFrame(data_list, columns=["Trial", "Insertion Size", "Time"])
	print(df)
	pd.set_option('display.max_rows', None)
	print(df.groupby('Insertion Size').mean().sort_values(by='Time'))

	sns.lineplot(df, x="Insertion Size", y="Time")
	plt.show()


def quick_vs_insertion():
	if os.path.isfile('quick_vs_insert.pkl'):
		with open('quick_vs_insert.pkl', 'rb') as f:
			results = pickle.load(f)
	else:
		results = {}

	trial_list = [(size, trial) for size, trial in itertools.product(range(500), range(100))]
	random.shuffle(trial_list)
	for size, trial in tqdm(trial_list):
			a = list(range(size))
			random.seed(trial)
			random.shuffle(a)
			start = time.time()
			insertion_sort(a)
			end = time.time()
			results[('Insertion', trial, size)] = (end - start)

			a = list(range(size))
			random.seed(trial)
			random.shuffle(a)
			start = time.time()
			quicksort(a, insert_size=size)
			end = time.time()
			results[('Quick', trial, size)] = (end - start)

			a = list(range(size))
			random.seed(trial)
			random.shuffle(a)
			start = time.time()
			quicksort(a)
			end = time.time()
			results[('Quick Opt', trial, size)] = (end - start)

			a = list(range(size))
			random.seed(trial)
			random.shuffle(a)
			start = time.time()
			a.sort()
			end = time.time()
			results[('Python', trial, size)] = (end - start)

	data_list = list([tuple([*x, y]) for x, y in results.items()])
	df = pd.DataFrame(data_list, columns=["Sort", "Trial",  "Size", "Time"])

	print(df)

	sns.lineplot(df, x="Size", y="Time", hue="Sort")
	plt.show()



if __name__ == '__main__':
	# partition_test()
	# quicksort_test()
	# main()
	# optimize_selection()
	quick_vs_insertion()


