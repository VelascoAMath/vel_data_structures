'''

This is an experiment to see if sorting the list of items to initialize an AVL tree offers better performance than not sorting.
According to our experiments, the answer is yes.
Sorting the items allows us to create a perfectly balanced binary search tree.
However, this is only if you directly initialize the tree using AVL.add_sorted().
If you repeatedly call the add() method, no advantage is offered over a randomly shuffled list of items
Because of these results, we will implement the __init__ method in AVL to offer a quick-insert flag which will quickly insert the items after sorting them at the cost of having to create a copy of the initial data


An example out the output showing that we can obtain more than 100 speed boost when inserting a large number of items
        Shuffled  Sorted DFS  Sorted Normal
count  10.000000   10.000000      10.000000
mean    5.133535    0.045005       5.135843
std     0.013956    0.006532       0.010714
min     5.115306    0.038255       5.117905
25%     5.124506    0.038898       5.127959
50%     5.132819    0.045282       5.136283
75%     5.136795    0.051171       5.145267
max     5.166247    0.051606       5.148310


@author: Alfredo Velasco
'''


from AVL import AVL
import time
import pandas as pd
import random
from tqdm import tqdm




def main():
	n = 2 ** 14 - 1
	results = pd.DataFrame()

	for i in tqdm(range(10)):
		l = list(range(n))

		# First test: Add sorted items in an iterative fashion like we normally would
		random.shuffle(l)
		start = time.time()
		a = AVL()
		a.add_items(l)
		end = time.time()
		# print(f"{a=}")

		results.at[i, 'Shuffled'] = end - start

		# Second test: Add the items in a DFS pattern
		start = time.time()
		a = AVL()
		l.sort()
		a.add_sorted(l)
		end = time.time()
		# print(f"{a=}")

		results.at[i, 'Sorted DFS'] = end - start

		# Third test: Add random items in an iterative fashion like we normally would
		random.shuffle(l)
		start = time.time()
		a = AVL()
		l.sort()
		a.add_items(l)
		end = time.time()
		# print(f"{a}")

		results.at[i, 'Sorted Normal'] = end - start


	print(results.describe())




if __name__ == '__main__':
	main()