'''

Checks to make sure that my new version of insert_into_list().

@author: Alfredo Velasco
'''



from BTree import insert_into_list
from tqdm import tqdm, trange
import random


def main():
	for b in tqdm([True, False], desc='bool loop'):
		for n in tqdm(list(range(1, 100)), desc='size loop', smoothing=0):
			for x in trange(1000, desc='random loop'):
				random.seed(x)
				s = list(range(n))
				random.shuffle(s)
				a = []
				for i in s:
					insert_into_list(i, a, b)

				s.sort(reverse=b)

				if s != a:
					raise Exception(f"{b=} {n=} {x=} provides us the wrong list! We have {a=} instead of {s}")





if __name__ == '__main__':
	main()