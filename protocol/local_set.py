#Inicialmente se usó un set() para almacenar los nodos locales, pero cuando hay
#muchos nodos comienzan a surgir problemas de concurrencia, por lo que ahora se
#usa una sección crítica para acceder al set. Todo esto ocurre porque los endpoints
#de FastAPI se corren de forma asíncrona.
import asyncio

class LocalSet:
    def __init__(self):
        self.local_nodes: set[str] = set()
        self.lock = asyncio.Lock()

    async def add(self, node_addr: str) -> None:
        async with self.lock:
            self.local_nodes.add(node_addr)

    async def remove(self, node_addr: str) -> None:
        async with self.lock:
            self.local_nodes.remove(node_addr)

    async def contains(self, node_addr: str) -> bool:
        async with self.lock:
            return node_addr in self.local_nodes

    async def get_all_nodes(self) -> list[str]:
        async with self.lock:
            return [node for node in self.local_nodes]
