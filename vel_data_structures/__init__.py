# https://stackoverflow.com/a/15833780
print("Hey! Why aren't you working!!!")

import inspect, testpkg
print(inspect.getmembers(testpkg, inspect.ismodule))

from BTree import BTree
from AVL import AVL, _Node
from AVL_Dict import AVL_Dict
