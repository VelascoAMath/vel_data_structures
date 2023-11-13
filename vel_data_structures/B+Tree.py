import collections
import random
from dataclasses import dataclass, field

import graphviz
from tqdm import tqdm

from vel_data_structures import List_Heap


WITH_GRAPHVIZ = False


@dataclass(order=True)
class _Node:
    b: int = 3
    items: List_Heap = field(default_factory=lambda: List_Heap(min=False))
    children: List_Heap = field(default_factory=lambda: List_Heap(min=False))

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
        return (
            f"_Node(b={self.b}, items={self.items}"
            + (f", children={self.children}" if len(self.children) > 0 else "")
            + ")"
        )


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
                for i in range(len(curr.items) - 1):
                    if curr[i] <= item < curr[i + 1]:
                        curr = curr.children[i + 1]
                        break
            path.append(curr)

        return path

    def insert(self, item):
        if self.n == 0:
            self.root = _Node(self.b)

        path = self._find_item(item)
        curr = path.pop()
        curr.insert(item)
        self.n += 1
        i = 0

        # We have space in the next node and the next node is a sibling
        if (
            curr.next is not None
            and len(curr.next.items) < self.b - 1
            and path
            and curr.next in path[-1].children
        ):
            curr.next.insert(curr.items.pop())

            curr = curr.next
            parent = path.pop()
            # Now we need to update the indexes
            while parent is not None:
                index = parent.children.index(curr)
                # This is the first child, and we don't need to update anything
                if index == 0:
                    return
                elif parent.items.item_list[index - 1] == curr[0]:
                    # Index is correct and we are done
                    return
                else:
                    if parent.items.item_list[index - 1] > curr[0]:
                        parent.items.item_list[index - 1] = curr[0]
                    curr = parent
                    if path:
                        parent = path.pop()
                    else:
                        parent = None

            return

        while curr.is_stuffed():
            new_sibling = _Node(self.b)
            new_sibling.insert(curr.items.pop())
            if not curr.is_internal():
                new_sibling.next = curr.next
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
            if WITH_GRAPHVIZ:
                self.to_graphviz("push" + str(i))
            i += 1

    def __contains__(self, item):
        path = self._find_item(item)
        return item in path[-1].items.item_list

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
        dot = graphviz.Digraph(
            "BP_Tree" + ("" if name is None else name),
            comment="The current B+Tree",
            format="pdf",
        )

        Q = collections.deque([self.root])

        while Q:
            curr = Q.popleft()
            dot.node(str(id(curr)), str(curr.items.item_list))
            for child in curr.children:
                dot.edge(str(id(curr)), str(id(child)))
                Q.append(child)

            # if curr.next is not None:
            #     dot.edge(str(id(curr)), str(id(curr.next)))

        dot.save()
        dot.render()


def main():
    n = 100
    for seed in tqdm(list(range(10000))):
        random.seed(seed)
        l = list(range(n))
        random.shuffle(l)
        print(l)
        b = BPTree(b=5)
        for index, i in enumerate(l):
            b.insert(i)
            if WITH_GRAPHVIZ:
                b.to_graphviz(str(index))
            if i not in b:
                raise Exception(f"{i} not in {b}!")

        if WITH_GRAPHVIZ:
            b.to_graphviz()
        for i in range(n):
            if i not in b:
                raise Exception(f"{i} not in {b}!")

        b_as_str = str(b)
        c_as_str = str(list(range(n)))
        print(f"{b=}")
        print(b)
        print()

        if b_as_str != c_as_str:
            raise Exception(f"{c_as_str} {b_as_str}")


if __name__ == "__main__":
    # import cProfile
    # import pstats
    #
    # with cProfile.Profile() as pr:
    main()

# stats = pstats.Stats(pr)
# stats.sort_stats(pstats.SortKey.TIME)
# stats.print_stats()
# stats.dump_stats(filename="needs_profiling.prof")
