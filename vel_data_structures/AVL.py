"""

A multi-set that is implemented using an AVL tree
https://en.wikipedia.org/wiki/AVL_tree

@author: Alfredo Velasco
"""

from collections import deque, defaultdict
from dataclasses import dataclass, field
from pprint import pprint
from tqdm import tqdm
from tqdm.auto import trange
import graphviz
import itertools
import os
import random


@dataclass
class _Node(object):
    """
    A node in the AVL tree
    """
    
    # The item the node holds
    item: int = None
    # The height of the subtree
    height: int = 1
    # Balance factor of this tree
    balance: int = 0
    # The left child
    left: int = None
    # The right child
    right: int = None
    
    def __repr__(self):
        return f"{self.item=} {self.height=} {self.balance=}"


def _bin_log(num):
    """
    Simple function to return two values.
    The log_2 of the inputted number (as an int) and the largest power of 2 less than or equal to the inputted number

    :param (int) num: the number we'll use to calculate
    :return int: log_2(num) rounded down to an int
    :return int: largest power of 2 that is <= num
    """
    if not isinstance(num, int) or num < 1:
        raise Exception(f"Inputted number({num}) must be a positive integer!")
    result = 1
    i = 0
    while result <= num:
        result *= 2
        i += 1
    return (i - 1, result // 2)


def _left_BST_split(i):
    """
	In order to create a BST which are inserted in this order
		   1
		  /  \
		 2    3
		/ \  /
	   4   5 6
	we need to figure out how many nodes need to be allocated to the right and left sides.
	This is a non-trivial task and we had to work hard to find these equations to find the number of items.
	This function will, given the number of items in a list, calculate the number of items that the left subtree will contain.
	In our example, our list has 6 items so our formula will say that there will be exactly 3 items to the left of the middle node
	:param (int) i: the number of items in the list to subdivide
	:return int: the number of items that the left subtree will contain
	"""
    num = _bin_log(i)[1]
    
    if (num >> 1) & i != 0:
        return (num >> 1) + 1 + (((num - 1) >> 1) - 1)
    else:
        return (num >> 1) + (((num - 1) >> 1) & i)


@dataclass
class AVL(object):
    """Represents an AVL tree"""
    
    _n: int = 0
    _root: _Node = field(default_factory=_Node)
    
    def __init__(self, items=None, fast_insert=True):
        """
        Initializes the tree with the items (if provided)

        :param list( items ) items: list of items to insert into the tree
        :param bool fast_insert: whether or not to sort the list of items in order to quickly build the tree at the cost of increasing the memory requirements
        """
        self.__post_init__()
        
        if items is not None:
            if fast_insert:
                l = list(items)
                l.sort()
                self.add_sorted(l)
            else:
                self.add_items(items)
    
    def __post_init__(self):
        super(AVL, self).__init__()
        self._n = 0
        self._root = None
        self._traversed_node_list = []
    
    def add(self, item):
        """
        Adds an item to the tree

        :param item: the item to be inserted
        """
        if self._n == 0:
            self._root = _Node(item)
        else:
            self._find_insertion_point(item)
            
            curr = self._traversed_node_list[-1]
            
            if item <= curr.item and curr.left is None:
                curr.left = _Node(item=item)
            elif curr.item <= item and curr.right is None:
                curr.right = _Node(item=item)
            else:
                raise Exception(
                    f"{self=} {item=}\nI didn't think about this situation!"
                )
            
            self._fix_heights(self._traversed_node_list)
        
        self._n += 1
    
    def add_items(self, l):
        """
        Add a list of items to the tree

        :param l: the list of items to insert
        """
        for i in l:
            self.add(i)
    
    def add_sorted(self, l):
        """
        Lets us insert a collection of sorted items quickly when the tree is being initialized

        :param l: the list of items to insert
        :raises Exception: if l is not sorted
        :raises Exception: if the tree is not empty
        """
        if self._n != 0:
            raise Exception("We can only quickly add sorted items into an empty tree!")
        
        if not l:
            return
        
        for i in range(1, len(l)):
            if l[i - 1] > l[i]:
                raise Exception(f"{l=} is not sorted!")
        
        # First, we need to do an in-order traversal to add the items in a linear fashion
        self._root = _Node()
        stack = [(0, len(l), self._root)]
        
        while stack:
            low, high, node = stack.pop()
            mid = _left_BST_split(high - low) + low
            item = l[mid]
            node.item = item
            self._n += 1
            sub_size = high - low
            
            height, rounded_log = _bin_log(sub_size)
            height += 1
            # If the second most significant bit is 1, balance is 0. Otherwise, balance is -1
            if height > 1 and (rounded_log // 2) & sub_size == 0:
                balance = -1
            else:
                balance = 0
            
            node.height = height
            node.balance = balance
            if mid + 1 < high:
                node.right = _Node()
                stack.append((mid + 1, high, node.right))
            
            if low < mid:
                node.left = _Node()
                stack.append((low, mid, node.left))
    
    def remove(self, item):
        """
        Removes an item from the tree

        :param item: the item to be deleted
        :raises KeyError: if item is not in the tree
        """
        if self._root is None:
            raise KeyError(f"Cannot remove from an empty tree!")
        
        if self._n == 1:
            self._root = None
            self._n = 0
            return
        
        if not self._traversed_node_list or self._traversed_node_list[-1].item != item:
            self._find_deletion_point(item)
        curr = self._traversed_node_list[-1]
        self._traversed_node_list.pop()
        if self._traversed_node_list:
            curr_parent = self._traversed_node_list[-1]
        else:
            curr_parent = None
        
        self._remove_node(curr, curr_parent)
        self._fix_heights(self._traversed_node_list)
        self._n -= 1
        self._traversed_node_list = []
    
    def _find_insertion_point(self, item):
        """
        This fills the traversed_node_list with a path from the root to a node whose child would contain the item

        :param item: the item to insert
        """
        
        curr = self._root
        self._traversed_node_list = []
        
        # Generic BST insertion
        while True:
            self._traversed_node_list.append(curr)
            if item < curr.item:
                if curr.left is None:
                    return
                else:
                    curr = curr.left
            elif item > curr.item:
                if curr.right is None:
                    return
                else:
                    curr = curr.right
            # curr is identical to item
            else:
                # If we have one empty child
                if curr.left is None or curr.right is None:
                    return
                # Otherwise, go where the tree is less balanced
                else:
                    #  Tree is right heavy
                    if curr.balance >= 0:
                        curr = curr.left
                    else:
                        curr = curr.right
    
    def _find_deletion_point(self, item):
        """
        This fills the traversed_node_list with a path from the root to a node whose child would contain the item

        :param item: the item to remove
        """
        
        curr = self._root
        self._traversed_node_list = []
        
        # Generic BST insertion
        while True:
            self._traversed_node_list.append(curr)
            if item < curr.item:
                if curr.left is None:
                    return
                else:
                    curr = curr.left
            elif item > curr.item:
                if curr.right is None:
                    return
                else:
                    curr = curr.right
            else:
                if curr.left is None and curr.right is None:
                    return
                elif curr.left is None and curr.right.item == item:
                    curr = curr.right
                elif curr.right is None and curr.left.item == item:
                    curr = curr.left
                else:
                    return
    
    def _remove_node(self, node, parent):
        """
        A method to the node and pass its value to the parent.
        This is the same as a delete operation in a BST

        :param node: the node we want to delete
        :param parent: the parent node of node
        :raises Exception: if node isn't a _Node or the parent is None
        """
        if not isinstance(node, _Node):
            raise Exception(
                f"The node must be of type _Node but is instead {type(node)}"
            )
        
        if node is None:
            raise Exception(f"The node is None!")
        
        if parent is None and node is not self._root:
            raise Exception(f"The parent is None!")
        
        if self._traversed_node_list is None:
            self._traversed_node_list = []
        
        # Case 1: node is leaf
        if node.height == 1:
            if parent.left is node:
                parent.left = None
            elif parent.right is node:
                parent.right = None
            else:
                raise Exception(f"{parent=} isn't a parent of {node=}!")
        # Get smallest element that's bigger than item
        elif node.right is not None:
            self._traversed_node_list.append(node)
            curr_parent = node
            curr = node.right
            while curr.left is not None:
                self._traversed_node_list.append(curr)
                curr_parent = curr
                curr = curr.left
            
            node.item = curr.item
            self._remove_node(curr, curr_parent)
        elif node.left is not None:
            self._traversed_node_list.append(node)
            curr_parent = node
            curr = node.left
            while curr.right is not None:
                self._traversed_node_list.append(curr)
                curr_parent = curr
                curr = curr.right
            
            node.item = curr.item
            self._remove_node(curr, curr_parent)
    
    def _fix_heights(self, node_list):
        """
        Balances all of the nodes in node_list
        :param node_list: list of nodes to adjust
        """
        for i in range(1, len(node_list)):
            if (
                node_list[i - 1].left is not node_list[i]
                and node_list[i - 1].right is not node_list[i]
            ):
                raise Exception(
                    f"Illegal node traversal! {node_list[i - 1]} is not the parent of {node_list[i]}!"
                )
        
        if node_list[0] is not self._root:
            raise Exception(f"{node_list[0]=} is not the root!")
        
        # Calculate the new heights
        for i in range(len(node_list) - 1, -1, -1):
            curr = node_list[i]
            if i > 0:
                self._fix_height(curr, node_list[i - 1])
            else:
                self._fix_height(curr)
    
    def _fix_height(self, node, parent=None):
        """
        Balances the node so its balance factor is within [-1, 1]
        :param _Node node: the node we'll balance
        :param _Node parent: the parent of node
        """
        self._calculate_height(node)
        self._calculate_balance(node)
        if node.balance == 2:
            # Scenario 2
            #    node
            #    /  \
            #        x1
            #          \
            #            x2
            if node.right is not None and node.right.balance >= 0:
                if node is self._root:
                    self._root = node.right
                else:
                    if parent.right is node:
                        parent.right = node.right
                    elif parent.left is node:
                        parent.left = node.right
                    # else:
                    # 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")
                
                temp = node.right
                node.right = temp.left
                temp.left = node
                self._calculate_height_and_balance(node)
                self._calculate_height_and_balance(temp.right)
                self._calculate_height_and_balance(temp)
            # Scenario 1
            #    node
            #    /  \
            #        x1
            #       /
            #      x3
            # elif node.right is not None and node.right.balance < 0:
            else:
                if node is self._root:
                    self._root = node.right.left
                else:
                    if parent.left is node:
                        parent.left = node.right.left
                    elif parent.right is node:
                        parent.right = node.right.left
                    # else:
                    # 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")
                temp = node.right.left
                node.right.left = temp.right
                temp.right = node.right
                node.right = temp.left
                temp.left = node
                self._calculate_height_and_balance(temp.left)
                self._calculate_height_and_balance(temp.right)
                self._calculate_height_and_balance(temp)
            
            # else:
            # 	raise Exception(f"This node {node} has a perfectly balanced right child!")
        
        if node.balance == -2:
            # Scenario 4
            #      node
            #     /
            #    x1
            #    /
            #   x2
            if node.left is not None and node.left.balance <= 0:
                if node is self._root:
                    self._root = node.left
                else:
                    if parent.left is node:
                        parent.left = node.left
                    elif parent.right is node:
                        parent.right = node.left
                    # else:
                    # 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")
                
                temp = node.left
                node.left = temp.right
                temp.right = node
                self._calculate_height_and_balance(node)
                self._calculate_height_and_balance(temp.left)
                self._calculate_height_and_balance(temp)
            # Scenario 3
            #    node
            #    /
            #   x1
            #     \
            #      x3
            else:
                if node is self._root:
                    self._root = node.left.right
                else:
                    if parent.left is node:
                        parent.left = node.left.right
                    elif parent.right is node:
                        parent.right = node.left.right
                    # else:
                    # 	raise Exception(f"Illegal node traversal! {parent} is not the parent of {node_list[i]}!")
                temp = node.left.right
                node.left.right = temp.left
                temp.left = node.left
                node.left = temp.right
                temp.right = node
                self._calculate_height_and_balance(temp.right)
                self._calculate_height_and_balance(temp.left)
                self._calculate_height_and_balance(temp)
            # else:
            # 	raise Exception(f"This node {node} has a perfectly balanced left child!")
    
    def _calculate_height(self, node):
        """
        Calculates the height of an inputted node
        Note that this assumes that the children have the correct heights
        :param _Node node: node whose height we'll calculate
        """
        if node is None:
            raise Exception("Can't calculate height on None!")
        if not isinstance(node, _Node):
            raise Exception(
                f"Passed in node must be _Node but is instead {type(node)}!"
            )
        
        if node.left is None:
            lh = 0
        else:
            lh = node.left.height
        if node.right is None:
            rh = 0
        else:
            rh = node.right.height
        
        node.height = max(1 + lh, 1 + rh)
    
    def _calculate_balance(self, node):
        """
        Calculates the balance of an inputted node
        Note that this assumes that the children have the correct balances

        :param _Node node: node whose balance we'll calculate
        """
        if node is None:
            raise Exception("Can't calculate balance on None!")
        if not isinstance(node, _Node):
            raise Exception(
                f"Passed in node must be _Node but is instead {type(node)}!"
            )
        
        if node.left is None:
            lh = 0
        else:
            lh = node.left.height
        if node.right is None:
            rh = 0
        else:
            rh = node.right.height
        
        node.balance = rh - lh
    
    def _calculate_height_and_balance(self, node):
        self._calculate_height(node)
        self._calculate_balance(node)
    
    def contains(self, item):
        """
        Indicates if you item is in the tree

        :param item: the item to find in the tree
        :return bool:  if the item was found in the tree
        """
        if self._root is None:
            return False
        
        self._find_deletion_point(item)
        return self._traversed_node_list[-1].item == item
    
    def clear(self):
        """
        Deletes all of the items in the tree
        """
        self._root = None
        self._n = 0
        self._traversed_node_list = []
    
    def __len__(self):
        """
        Returns the number of items in the tree

        :return: int: the number of items in the tree
        """
        return self._n
    
    def items_yield(self):
        """
        Generator function that iterates DFS through the items in the tree

        :return item: the items in the tree
        """
        if self._root is None:
            yield from []
        else:
            discovered = set()
            stack = [self._root]
            
            while stack:
                node = stack[-1]
                if node is None:
                    raise Exception("This tree has a None element!")
                if not isinstance(node, _Node):
                    raise Exception("This tree has a non-_Node {node} element!")
                
                discovered.add(id(node))
                
                inserted_left = False
                inserted = False
                
                if node.left is not None and id(node.left) not in discovered:
                    stack.append(node.left)
                    inserted_left = True
                    inserted = True
                
                if (
                    not inserted_left
                    and node.right is not None
                    and id(node.right) not in discovered
                ):
                    stack.append(node.right)
                    if not inserted:
                        item = stack.pop(-2)
                        yield item
                    inserted = True
                
                if not inserted:
                    item = stack.pop()
                    yield item
    
    def __contains__(self, item):
        """
        Wrapper for the contains method
        """
        return self.contains(item)
    
    def __iter__(self):
        """
        A DFS iterator through the tree
        """
        self.discovered = set()
        if self._root is None:
            self.stack = []
        else:
            self.stack = [self._root]
        return self
    
    def __next__(self):
        while self.stack:
            node = self.stack[-1]
            if node is None:
                raise Exception("This tree has a None element!")
            if not isinstance(node, _Node):
                raise Exception("This tree has a non-_Node {node} element!")
            
            self.discovered.add(id(node))
            
            inserted_left = False
            inserted = False
            
            if node.left is not None and id(node.left) not in self.discovered:
                self.stack.append(node.left)
                inserted_left = True
                inserted = True
            
            if (
                not inserted_left
                and node.right is not None
                and id(node.right) not in self.discovered
            ):
                self.stack.append(node.right)
                if not inserted:
                    return self.stack.pop(-2).item
                inserted = True
            
            if not inserted:
                return self.stack.pop().item
        
        raise StopIteration
    
    def __dfs_str__(self, node=None):
        """
        Returns a DFS representation of the tree

        :param _Node node: a node which we'll print out along with its children
        :return: a string representation of the tree
        :rtype: str
        """
        if node is None:
            return ""
        
        result = node.__repr__()
        
        if node.left is not None:
            result += f", L({self.__dfs_str__(node.left)})"
        if node.right is not None:
            result += f", R({self.__dfs_str__(node.right)})"
        
        return result
    
    def __terminal_str__(self):
        """
        Returns a visual representation of the tree that can be printed in the terminal

        :return: a string representation of the tree
        :rtype: str
        """
        if self._root is None:
            return ""
        
        # The width of the final result
        max_x = 0
        min_y = 0
        max_y = 0
        
        # node, y, level
        node_list = [(self._root, 0, 0)]
        # Maps each tree level to the size of its largest node (when converted to a str)
        level_to_max_len = defaultdict(int)
        
        # We need to iterate through the tree to fill out level_to_max_len and to find out the size of the full display
        while node_list:
            node, y, level = node_list.pop()
            # Update the largest item in the level
            level_to_max_len[level] = max(level_to_max_len[level], len(str(node.item)))
            min_y = min(y, min_y)
            max_y = max(y, max_y)
            
            if node.right is not None:
                node_list.append((node.right, y - 2 ** (node.height - 2), level + 1))
            
            if node.left is not None:
                node_list.append((node.left, y + 2 ** (node.height - 2), level + 1))
        
        # Get the total width
        for i in level_to_max_len.values():
            max_x += 1 + i
        # The last level doesn't count
        max_x -= 1
        
        result = [[" "] * max_x for i in range(max_y - min_y + 1)]
        
        # print(f"{min_y=} {max_y=} {max_x=}")
        node_list = [(self._root, 0, 0, 0)]
        while node_list:
            node, x, y, level = node_list.pop()
            # print(f"{node=} {x=} {y=} {level=}")
            node_str = str(node.item).rjust(level_to_max_len[level])
            
            for i in range(level_to_max_len[level]):
                result[y - min_y][x + i] = node_str[i]
            
            stem_height = 2 ** (node.height - 2)
            if node.right is not None:
                node_list.append(
                    (
                        node.right,
                        x + level_to_max_len[level] + 1,
                        y - stem_height,
                        level + 1,
                    )
                )
                
                for i in range(1, stem_height):
                    result[y - i - min_y][x + level_to_max_len[level] - 1] = "|"
                result[y - stem_height - min_y][x + level_to_max_len[level] - 1] = "+"
                result[y - stem_height - min_y][x + level_to_max_len[level]] = ">"
            
            if node.left is not None:
                node_list.append(
                    (
                        node.left,
                        x + level_to_max_len[level] + 1,
                        y + stem_height,
                        level + 1,
                    )
                )
                
                for i in range(1, stem_height):
                    result[y + i - min_y][x + level_to_max_len[level] - 1] = "|"
                result[y + stem_height - min_y][x + level_to_max_len[level] - 1] = "+"
                result[y + stem_height - min_y][x + level_to_max_len[level]] = ">"
        
        actual_result = ""
        for line in result:
            for c in line:
                actual_result += c
            actual_result += "\n"
        
        return actual_result
    
    def __repr__(self):
        if self._root is None:
            return "AVL()"
        
        return f"AVL(\n{self.__terminal_str__()})"
    
    def __str__(self):
        l = [f"{item}" for item in self]
        return "{" + ", ".join(l) + "}"
    
    def to_dot(self, f_name):
        """

        This method writes out the AVL to a .dot file and a visualization by graphviz.

        :param str f_name: the name of the files. If no extension is provided, the output will be in .pdf
        """
        
        filen, file_ext = os.path.splitext(f_name)
        
        if file_ext == "":
            file_ext = ".pdf"
        
        dot = graphviz.Digraph(
            "AVL",
            filename=filen,
            format=file_ext[1:],
            node_attr={"fontname": "Helvetica,Arial,sans-serif"},
        )
        
        dot.attr(rankdir="UP")
        
        if self._root is not None:
            stack = [(self._root, 0)]
            
            while stack:
                node, node_id = stack.pop()
                
                if node is None:
                    raise Exception("This tree has a None element!")
                if not isinstance(node, _Node):
                    raise Exception("This tree has a non-_Node {node} element!")
                
                dot.node(f"n{node_id}", shape="circle", label=f"{node.item}")
                
                if node.left is not None:
                    l_node_id = node_id + 1
                    dot.edge(f"n{node_id}", f"n{l_node_id}", color="red")
                    
                    stack.append((node.left, l_node_id))
                
                if node.right is not None:
                    # The left subtree can only contain at most 2 ^ (node.height - 1) nodes
                    r_node_id = node_id + (1 << (node.height - 1))
                    dot.edge(f"n{node_id}", f"n{r_node_id}", color="blue")
                    
                    stack.append((node.right, r_node_id))
        
        dot.render()
    
    def _verify_itself(self, node=None):
        """
        Verifies that the tree is balanced, ordered, and has the correct balance factor and height
        """
        if node is None:
            node = self._root
        if self._root is None:
            return
        
        prev_balance = node.balance
        prev_height = node.height
        
        if node.left is not None:
            if node.left.item > node.item:
                raise Exception(f"{node} > {node.left} (its left child)!")
            self._verify_itself(node.left)
        if node.right is not None:
            if node.right.item < node.item:
                raise Exception(f"{node} > {node.right} (its right child)!")
            self._verify_itself(node.right)
        
        self._calculate_height_and_balance(node)
        
        if node.balance != prev_balance:
            raise Exception(f"{node} should have a balance of {node.balance}!")
        if node.height != prev_height:
            raise Exception(f"{node} should have a height of {node.height}!")
        if node.balance < -1 or node.balance > 1:
            raise Exception(f"{node} should have a balance in [-1, 1]!")


def main():
    # t = AVL(list(range(512 - 1)))
    # t.to_dot('Trash')
    # return
    
    # Random insertions of lists
    #
    def random_insertion_test():
        for x in tqdm(range(10000), desc="Insertion"):
            s = list(range(100))
            l = s[:]
            random.seed(x)
            random.shuffle(l)
            t = AVL(l, False)
            r = list(t)
            
            if r != s:
                raise Exception(f"{x=} results in an error!")
            
            if len(r) != len(s):
                raise Exception(f"{x=} results in an error!")
    
    # Random duplicates
    #
    def random_duplicate_test():
        for x in tqdm(range(10000), desc="Duplicates"):
            random.seed(x)
            l = [random.randint(1, 100) for x in range(1000)]
            s = l[:]
            t = AVL()
            t.add_items(l)
            s.sort()
            r = list(t)
            if r != s:
                raise Exception(f"{x=} results in an error!\n{r}\n{s}")
            if len(r) != len(s):
                raise Exception(f"{x=} results in an error!")
    
    # Check the contains
    #
    def contains_test():
        for x in tqdm(range(10000), desc="Contains"):
            random.seed(x)
            s = set(random.sample(list(range(1000)), 100))
            c = set(range(1000)) - s
            
            t = AVL(s, True)
            for i in s:
                if i not in t:
                    raise Exception(f"{x=} causes an error!")
            for i in c:
                if i in t:
                    raise Exception(f"{x=} causes an error!")
    
    def remove_test():
        # Test the remove method
        #
        for n in tqdm(list(itertools.chain(range(20), [50, 100])), desc="Size"):
            t = AVL()
            for x in tqdm(range(10000), desc="Remove"):
                t.clear()
                random.seed(x)
                a = set([random.randint(0, n) for x in range(n)])
                b = set([random.randint(0, n) for x in range(n)])
                
                t.add_items(a)
                t._verify_itself()
                
                # print(t)
                for i in b:
                    if i in t:
                        t.remove(i)
                        t._verify_itself()
                
                s = a - b
                r = set(t)
                if r != s:
                    raise Exception(f"{x=} results in an error!\n{r}\n{s}")
                if len(r) != len(s):
                    raise Exception(f"{x=} results in an error!")
        
        # Test the remove method
        #
        for n in tqdm([1000, 10000], desc="Size"):
            t = AVL()
            for x in tqdm(range(1000 // n), desc="Remove"):
                t.clear()
                random.seed(x)
                a = set([random.randint(0, n) for x in range(n)])
                b = set([random.randint(0, n) for x in range(n)])
                
                t.add_sorted(sorted(list(a)))
                t._verify_itself()
                
                for i in b:
                    if i in t:
                        t.remove(i)
                        t._verify_itself()
                
                s = a - b
                r = set(t)
                if r != s:
                    raise Exception(f"{x=} results in an error!\n{r}\n{s}")
                if len(r) != len(s):
                    raise Exception(f"{x=} results in an error!")
    
    random_insertion_test()
    random_duplicate_test()
    contains_test()
    remove_test()


if __name__ == "__main__":
    main()
