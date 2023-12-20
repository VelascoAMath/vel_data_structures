# For some reason, Python gives import errors when trying to import from the current directory. Although a bit hacky, this should fix those issues
# https://stackoverflow.com/a/44230992
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


from .BTree import BTree
from .BHeap import BHeap
from .AVL import AVL
from .AVL_Dict import AVL_Dict
from .AVL_Set import AVL_Set    
from .List_Heap import List_Heap
