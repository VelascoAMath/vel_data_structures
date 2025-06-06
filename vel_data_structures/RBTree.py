import dataclasses
import random
from typing import Self, Iterable


@dataclasses.dataclass
class _Node[T]:
    item: T = None
    is_red: bool = True
    left: Self = None
    right: Self = None
    
    def black_path_length(self) -> int:
        # None nodes are considered to be black
        if self.left is None and self.right is None:
            if self.is_red:
                return 1
            else:
                return 2
        if self.left is None:
            if self.is_red:
                return self.right.black_path_length()
            else:
                return 1 + self.right.black_path_length()
        
        if self.is_red:
            return self.left.black_path_length()
        else:
            return 1 + self.left.black_path_length()
    
    def verify(self) -> bool:
        if self.left is None and self.right is None:
            return True
        
        if self.left is None:
            if self.is_red and self.right.is_red:
                return False
            
            return self.right.black_path_length() == 1
        
        if self.right is None:
            if self.is_red and self.left.is_red:
                return False
            return self.left.black_path_length() == 1
        
        if self.is_red and (self.left.is_red or self.right.is_red):
            return False
        
        return self.left.black_path_length() == self.right.black_path_length()
    
    def __repr__(self):
        return f"Node(item={self.item}, c={'R' if self.is_red else 'B'}" + (
            (", left=" + self.left.__repr__()) if self.left is not None else '') + (
            (", right=" + self.right.__repr__()) if self.right is not None else '') + ")"


@dataclasses.dataclass
class RBTree[T]:
    _root: _Node = None
    _n: int = 0
    
    def __init__(self, items: Iterable[T] = None):
        if items is not None:
            for item in items:
                self.insert(item)
    
    def _find_search_path(self, item: T) -> list[_Node]:
        """
        This will find the path to find an item in the tree
        This path doesn't actually check to see if the item is in the tree,
        so it just follows the best sequences of nodes to search
        """
        path = [self._root]
        
        while True:
            # Go left
            if item < path[-1].item:
                if path[-1].left is None:
                    return path
                else:
                    path.append(path[-1].left)
            # Found the item
            elif item == path[-1].item:
                return path
            # Go right
            else:
                if path[-1].right is None:
                    return path
                else:
                    path.append(path[-1].right)
    
    def _find_insertion_path(self, item: T) -> list[_Node]:
        """
        This will find the path to insert an item into the tree
        """
        path = [self._root]
        
        while True:
            if item < path[-1].item:
                if path[-1].left is None:
                    return path
                else:
                    path.append(path[-1].left)
            else:
                if path[-1].right is None:
                    return path
                else:
                    path.append(path[-1].right)
    
    def verify(self):
        if self._n == 0:
            return True
        return self._root.verify()
    
    def insert(self, item: T):
        if self._n == 0:
            self._root = _Node(item, False)
        else:
            path = self._find_insertion_path(item)
            child = _Node(item)
            parent = path[-1]
            if item < parent.item:
                parent.left = child
            else:
                parent.right = child
            
            # Tree invariant not held
            # Need to rebalance and/or recolor
            while parent.is_red and child.is_red:
                
                # Case 4
                # Parent is root
                if parent is self._root:
                    parent.is_red = False
                    return
                
                # Let's get the graphparent and uncle
                grandparent = path[-2]
                if grandparent.left is parent:
                    uncle = grandparent.right
                else:
                    uncle = grandparent.left
                
                # Case 2
                # Uncle is also red
                # A simple recoloring can fix a few layers
                # We will need to navigate up the tree since the upper layers may also need readjustments
                if uncle is not None and uncle.is_red:
                    parent.is_red = False
                    uncle.is_red = False
                    grandparent.is_red = True
                    child = grandparent
                    path.pop()
                    path.pop()
                    if not path:
                        break
                    parent = path[-1]
                    continue
                
                # Case 5
                # LR pattern
                if parent is grandparent.left and child is parent.right:
                    parent.right = child.right
                    child.right = child.left
                    child.left = parent.left
                    parent.left = child
                    parent.item, child.item = child.item, parent.item
                # RL pattern
                if parent is grandparent.right and child is parent.left:
                    parent.item, child.item = child.item, parent.item
                    parent.left = child.left
                    child.left = child.right
                    child.right = parent.right
                    parent.right = child
                # Case 6
                # Right leaning children
                elif parent is grandparent.left and child is parent.left:
                    parent.item, grandparent.item = grandparent.item, parent.item
                    grandparent.left = child
                    parent.left = parent.right
                    parent.right = grandparent.right
                    grandparent.right = parent
                    break
                # Left leaning children
                else:
                    # Rotate the trees
                    parent.item, grandparent.item = grandparent.item, parent.item
                    grandparent.right = child
                    parent.right = parent.left
                    parent.left = grandparent.left
                    grandparent.left = parent
                    break
        
        self._n += 1
        return item
    
    def remove(self, item: T):
        if self._n == 0:
            raise KeyError(f"Cannot remove {item} from an empty tree!")
        if self._n == 1:
            self._root = None
            self._n = 0
        
        path = self._find_search_path(item)
        if path[-1].item != item:
            raise KeyError(f"{item} not found in the tree!")
        
        self._n -= 1
        while True:
            child = path[-1]
            parent = path[-2]
            if child is parent.left:
                sibling = parent.right
                parent.left = None
            else:
                sibling = parent.left
                parent.right = None
            
            if sibling is None:
                close_nephew = None
                distant_nephew = None
            else:
                if child is parent.left:
                    close_nephew = sibling.left
                    distant_nephew = sibling.right
                else:
                    close_nephew = sibling.right
                    distant_nephew = sibling.left
            
            # Case D2
            # All nodes are blacks
            if not parent.is_red and (sibling is None or (not sibling.is_red and ((close_nephew is None or not close_nephew.is_red) and (distant_nephew is None or not distant_nephew.is_red)) ) ):
                if sibling is not None:
                    sibling.is_red = True
                    path.pop()
                    break
                else:
                    break
            
            # Case D3
            # The parent and siblings are red while the nephews are black
            if parent.is_red and sibling is not None and sibling.is_red and (close_nephew is None or not close_nephew.is_red) and (distant_nephew is None or not distant_nephew.is_red):
                pass
            
        
        
        
    
    def __contains__(self, item: T):
        if self._n == 0:
            return False
        path = self._find_search_path(item)
        return path[-1].item == item
    
    def __iter__(self):
        self._iter_stack = []
        self._discovered = set()
        
        curr = self._root
        while curr is not None:
            self._iter_stack.append(curr)
            curr = curr.left
        return self
    
    def __next__(self):
        
        while self._iter_stack:
            curr = self._iter_stack[-1]
            if curr.left is not None and id(curr.left) not in self._discovered:
                self._iter_stack.append(curr.left)
            elif id(curr) not in self._discovered:
                self._discovered.add(id(curr))
                return curr.item
            elif curr.right is not None and id(curr.right) not in self._discovered:
                self._iter_stack.append(curr.right)
            else:
                self._iter_stack.pop()
        
        raise StopIteration


def main():
    t = RBTree()
    l = list(range(100))
    random.shuffle(l)
    print(l)
    
    for i in l:
        t.insert(i)
        print(t)
        print(list(t))


if __name__ == '__main__':
    main()
