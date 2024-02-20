import queue
import threading



class BufferStream:
    """
    A class for buffering and streaming data items.

    Attributes:
        items (queue.Queue): A thread-safe queue for storing data items.
        _stop_event (threading.Event): An event to signal stopping the generator.
    """
    def __init__(self):
        self.items = queue.Queue()
        self._stop_event = threading.Event()

    def add(self, item: str) -> None:
        """Add an item to the buffer."""
        self.items.put(item)

    def stop(self) -> None:
        """Signal to stop the buffer stream."""
        self._stop_event.set()

    def snapshot(self) -> list:
        """Take a snapshot of all items in the buffer without exhausting it.

        Returns:
            list: A list of all items currently in the buffer.
        """
        all_items = []
        temp_storage = []

        # Temporarily dequeue items to snapshot them.
        while not self.items.empty():
            item = self.items.get_nowait()
            all_items.append(item)
            temp_storage.append(item)

        # Re-queue the items.
        for item in temp_storage:
            self.items.put(item)

        return all_items

    def gen(self):
        """
        Generate items from the buffer, yielding them one at a time.

        Continues yielding items until the buffer is empty and stop has been signaled.
        """
        while not self._stop_event.is_set() or not self.items.empty():
            try:
                yield self.items.get(timeout=0.1)
            except queue.Empty:
                continue




# import queue
# import threading


# class BufferStream:
#     """
#     A class for buffering and streaming data items.

#     Attributes:
#         items (queue.Queue): A thread-safe queue for storing data items.
#         _stop_event (threading.Event): An event to signal stopping the generator.
#     """
#     def __init__(self):
#         self.items = queue.Queue()
#         self._stop_event = threading.Event()

#     def add(self, item: str) -> None:
#         """Add an item to the buffer."""
#         self.items.put(item)

#     def stop(self):
#         """Signal to stop the buffer stream."""
#         self._stop_event.set()

#     def snapshot(self) -> list:
#         """Take a snapshot of all items in the buffer without exhausting it.

#         Returns:
#             list: A list of all items currently in the buffer.
#         """
#         all_items = []
#         temp_storage = []

#         # Temporarily dequeue items to snapshot them.
#         while not self.items.empty():
#             item = self.items.get_nowait()
#             all_items.append(item)
#             temp_storage.append(item)

#         # Re-queue the items.
#         for item in temp_storage:
#             self.items.put(item)

#         return all_items

#     def gen(self):
#         """Generate items from the buffer, yielding them one at a time."""
#         while not self._stop_event.is_set():
#             try:
#                 yield self.items.get(timeout=0.1)
#             except queue.Empty:
#                 continue
