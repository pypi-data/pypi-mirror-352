from collections import deque


class Queue:
    def __init__(self):
        """
        A deque wrapper for ease of use.
        It is thread-safe according to Python docs.

        The queue is simply a "buffer"

        """
        self.__queue = deque()

    def push(self, item):
        self.__queue.append(item)

    def pop(self):
        if self.__queue.__len__() == 0:
            return None
        return self.__queue.popleft()

    def front(self):
        if self.__queue.__len__() == 0:
            return None
        return self.__queue.__getitem__(0)

    def back(self):
        if self.__queue.__len__() == 0:
            return None
        return self.__queue.__getitem__(-1)

    def available(self):
        return self.__len__() > 0

    def __len__(self):
        return self.__queue.__len__()

    def __str__(self):
        return self.__queue.__str__()

    def __repr__(self):
        return self.__queue.__repr__()

    def __getitem__(self, index):
        return self.__queue.__getitem__(index)

    @property
    def data(self):
        return self.__queue
