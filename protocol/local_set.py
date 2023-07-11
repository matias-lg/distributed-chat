from typing import TypeVar, Generic

T = TypeVar("T")
class LocalSet(Generic[T]):
    def __init__(self):
        self.local_items: set[T] = set()

    def add(self, element: T) -> None:
        self.local_items.add(element)

    def remove(self, element: T) -> None:
        self.local_items.remove(element)

    def contains(self, element: T) -> bool:
        return element in self.local_items

    def get_all_elements(self) -> list[T]:
        return [ele for ele in self.local_items]