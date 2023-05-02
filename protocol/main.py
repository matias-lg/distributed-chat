import os
import random
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from .local_set import LocalSet
from .utils import print_receive_message, inform_node


class NodeMsg(BaseModel):
    sender: str = ""
    new_node_address: str = ""


# set que contiene las direcciones de los nodos conocidos
local_nodes = LocalSet()

# Leer las variables de entorno que contienen al nodo conocido
KNOWN_NODE_IP = os.environ.get("KNOWN_NODE_IP")
KNOWN_NODE_PORT = os.environ.get("KNOWN_NODE_PORT")
THIS_NODE_NAME = os.environ.get("NODE_NAME")
THIS_NODE_IP = os.environ.get("NODE_IP")
THIS_NODE_PORT = os.environ.get("NODE_PORT")
THIS_NODE_ADDR = os.environ.get("NODE_ADDR") or "IGNORE"

app = FastAPI()


@app.get("/")
def root():
    return {"message": f"Tarea 1 de sistemas distribuidos",
            "node_name": THIS_NODE_NAME,
            "node_addr": THIS_NODE_ADDR
            }


@app.get("/nodes")
async def get_nodes():
    return {"nodes": await local_nodes.get_all_nodes()}


@app.post("/nodes")
async def add_node(node_msg: NodeMsg):
    new_address = node_msg.new_node_address
    sender = node_msg.sender
    if await local_nodes.contains(new_address):
        return {"message": "El nodo ya es conocido"}
    if new_address == THIS_NODE_ADDR:
        return {"message": "No me envíes a mi mismo"}

    print_receive_message(sender, new_address)
    await local_nodes.add(new_address)
    # Avisarle a nuestros conocidos de la existencia del nuevo nodo
    for node in await local_nodes.get_all_nodes():
        if node not in [sender, new_address]:
            inform_node(node, new_address, THIS_NODE_ADDR)
    # Avisarle de mi existencia al nuevo nodo, si es que él no se envió a si mismo
    # (eso significa que ya me conoce)
    if sender != new_address:
        inform_node(new_address, THIS_NODE_ADDR, THIS_NODE_ADDR)
    return {"message": "Nodo agregado exitosamente"}


@app.on_event("startup")
async def initial_setup():
    # El primer nodo se inicia sin nodos conocidos
    if KNOWN_NODE_IP != "IGNORE" and KNOWN_NODE_PORT != "IGNORE":
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        known_address: str = f"{KNOWN_NODE_IP}:{KNOWN_NODE_PORT}"
        await local_nodes.add(known_address)
        inform_node(known_address, THIS_NODE_ADDR, THIS_NODE_ADDR)
    print(f"{THIS_NODE_NAME} iniciado con dirección {THIS_NODE_ADDR}")


@app.on_event("startup")
@repeat_every(seconds=30)
# Cada 30 segundos informaremos a un nodo aleatorio de la existencia de otro nodo aleatorio, para evitar que por un error en la red un nodo quede aislado
async def randomnly_inform():
    all_nodes = await local_nodes.get_all_nodes()
    if len(all_nodes) < 2:
        return
    random_dest_node = random.choice(all_nodes)
    random_new_node = random.choice(all_nodes + [THIS_NODE_ADDR])
    while random_new_node == random_dest_node:
        random_new_node = random.choice(all_nodes + [THIS_NODE_ADDR])
    inform_node(random_dest_node, random_new_node, THIS_NODE_ADDR)
