import collections
from dataclasses import dataclass, field

import graphviz

from vel_data_structures import List_Heap


@dataclass(order=True)
class _Node:
    b: int = 3
    items: List_Heap = field(default_factory=lambda: List_Heap(min=False))
    children: List_Heap = field(default_factory=lambda : List_Heap(min=False))

    def __post_init__(self):
        self.next = None

    def __getitem__(self, key):
        return self.items.__getitem__(key)

    def insert(self, item):
        self.items.insert(item)

    def pop(self):
        return self.items.pop()

    def pop_child(self):
        return self.children.pop()
    def is_internal(self):
        return len(self.children) != 0
    def is_stuffed(self):
        return len(self.items) >= self.b

    def insert_child(self, child):
        if child not in self.children:
            self.children.insert(child)

    def __repr__(self):
        return f"_Node(b={self.b}, items={self.items}" + (f", children={self.children}" if len(self.children) > 0 else "") + ")"

@dataclass
class BPTree:
    b: int = 3
    n: int = 0
    root: _Node = None

    def _find_item(self, item):
        path = [self.root]
        curr = self.root

        while curr.is_internal():
            if item < curr.items[0]:
                curr = curr.children[0]
            elif item >= curr.items[-1]:
                curr = curr.children[-1]
            else:
                if item < curr.items[0]:
                    curr = curr.children[0]
                else:
                    for i in range(len(curr.items) - 1):
                        if curr[i] <= item <= curr[i + 1]:
                            curr = curr.children[i + 1]
                            break
            path.append(curr)

        return path

    def insert(self, item):
        if self.n == 0:
            self.root = _Node(self.b)

        path = self._find_item(item)
        curr = (path.pop())
        curr.insert(item)
        self.n += 1
        i = 0

        while curr.is_stuffed():
            new_sibling = _Node(self.b)
            new_sibling.insert(curr.items.pop())
            if not curr.is_internal():
                curr.next = new_sibling
            if curr.is_internal():
                new_sibling.insert_child(curr.children.pop())
                new_sibling.insert_child(curr.children.pop())

            if curr == self.root:
                parent = _Node(self.b)
                self.root = parent
            else:
                parent = path.pop()

            if curr.is_internal():
                parent.insert(curr.pop())
                parent.insert_child(curr)
                parent.insert_child(new_sibling)
            else:
                parent.insert_child(curr)
                parent.insert_child(new_sibling)
                parent.insert(new_sibling[0])
            curr = parent
            i += 1

    def __str__(self):
        curr = self.root
        while curr.is_internal():
            curr = curr.children[0]

        result = []
        while curr is not None:
            result.extend(curr.items)
            curr = curr.next
        return str(result)

    def to_graphviz(self, name=None):
        dot = graphviz.Digraph('BP_Tree' + ('' if name is None else name), comment='The current B+Tree', format="pdf")

        Q = collections.deque([self.root])

        while Q:
            curr = Q.popleft()
            dot.node(str(id(curr)), str(curr.items.item_list))
            for child in curr.children:
                dot.edge(str(id(curr)), str(id(child)))
                Q.append(child)


        dot.save()
        dot.render()





def main():
    b = BPTree()
    for i in range(100):
        b.insert(i)

    print(f"{b=}")
    print(b)
    b.to_graphviz()


if __name__ == "__main__":
    main()
