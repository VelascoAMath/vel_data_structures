import dataclasses

from vel_data_structures import List_Heap


@dataclasses.dataclass
class _Node:
	start: int = None
	end: int = None
	items: List_Heap = dataclasses.field(default_factory=lambda: List_Heap(min=False))
	
	def add(self, start: int, end: int):
		if self.start is None and self.end is None:
			self.start = start
			self.end = end
		else:
			self.start = min(self.start, start)
			self.end = max(self.end, end)
		
		self.items.insert((start, end))
	
	def __iter__(self):
		return self.items.__iter__()
	def __contains__(self, item: int):
		if item < self.start:
			return False
		if item >= self.end:
			return False


@dataclasses.dataclass
class Ranges:
	_root: _Node = dataclasses.field(default_factory=_Node)
	
	def add(self, start: int, end: int):
		self._root.add(start, end)
	
	def __contains__(self, item):
		return any(item in n for n in self._root)


def main():
	r = Ranges()
	
	r.add(0, 3)
	r.add(3, 4)
	
	if 3 in r:
		print(r)


if __name__ == '__main__':
	main()
