#Inicialmente se usó un set() para almacenar los nodos locales, pero cuando hay
#muchos nodos comienzan a surgir problemas de concurrencia, por lo que ahora se
#usa una sección crítica para acceder al set. Todo esto ocurre porque los endpoints
#de FastAPI se corren de forma asíncrona.
import asyncio
from typing import TypeVar, Generic

T = TypeVar("T")
class LocalSet(Generic[T]):
    def __init__(self):
        self.local_items: set[T] = set()
        self.lock = asyncio.Lock()

    async def add(self, element: T) -> None:
        async with self.lock:
            self.local_items.add(element)

    async def remove(self, element: T) -> None:
        async with self.lock:
            self.local_items.remove(element)

    async def contains(self, element: T) -> bool:
        async with self.lock:
            return element in self.local_items

    async def get_all_elements(self) -> list[T]:
        async with self.lock:
            return [ele for ele in self.local_items]