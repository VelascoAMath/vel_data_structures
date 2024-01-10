'''
A ring buffer.
This is a queue that can hold only n items at most.

@author: Alfredo Velasco
'''

class Ring_Buffer(object):


    """A ring buffer of size n"""
    def __init__(self, capacity):
        '''
        Creates an empty ring buffer with the specified capacity.
        '''
        super(Ring_Buffer, self).__init__()
        self.capacity = capacity
        self.first = 0
        self.last = 0
        self.size = 0
        self.buffer = [0 for i in range(capacity)]
    


    def capacity(self):
        '''
        Returns the capacity of this ring buffer.
        
        :returns int capacity: the capacity
        '''
        return self.capacity

    def size():
        '''
        Returns the number of items currently in this ring buffer.
        
        :returns int size: the number of items in the queue
        '''
        
        return self.size

    def isEmpty(self):
        '''
        Is this ring buffer empty (size equals zero)?
        
        :returns bool: is size is 0
        '''
        return self.size == 0

    def isFull(self):
        '''
        Is this ring buffer full (size equals capacity)?
    
        :returns bool: if size == capacity
        '''
        return self.size == self.capacity

    def enqueue(self, x):
        '''
        Adds item x to the end of this ring buffer.

        :param x: the item to insert
        :raises Exception: if the ring buffer is full
        '''
        if (self.isFull()):
            raise Exception("RingBuffer is already full and cannot enqueue!")
        
        self.size += 1
        self.buffer[self.last] = x
        self.last = (self.last + 1) % self.capacity

    def dequeue(self):
        '''
        Deletes and returns the item at the front of this ring buffer.

        :returns item: the first item in the queue
        :raises Exception: if the ring buffer is empty
        '''
        if (self.isEmpty()):
            raise Exception("RingBuffer is empty and cannot dequeue!")
        self.size -= 1
        item = self.buffer[self.first]
        self.first = (self.first + 1) % self.capacity
        return item

    def peek(self):
        '''
        Returns the item at the front of this ring buffer.

        :returns item: the first item in the queue
        :raises Exception: if the ring buffer is empty
        '''
        if self.isEmpty():
            raise Exception("Cannot peek at an empty ring buffer!")
        
        return self.buffer[self.first]

    def __len__(self):
        return self.size



def main():
    n = 6

    buffer = Ring_Buffer(n)
    for i in range(1, n + 1):
        buffer.enqueue(i)
    t = buffer.dequeue()
    buffer.enqueue(t)

    while len(buffer) >= 2:
        x = buffer.dequeue()
        y = buffer.dequeue()
        buffer.enqueue(x + y)
    print(buffer.peek())


if __name__ == '__main__':
    main()
